"""
WatermarkTool v3.1 - Flask + Pillow + FFmpeg direto (sem MoviePy)
=================================================================
FFmpeg e chamado via subprocess - 10-50x mais rapido que MoviePy.
Progresso em tempo real via SSE (Server-Sent Events).
Animacoes de texto e logo em video via filtros FFmpeg.
"""

from io import BytesIO
import os, sys, re, json, math, time, uuid, shutil, zipfile
import tempfile, threading, datetime, subprocess, urllib.request
from flask import (Flask, render_template, request, send_file,
                   jsonify, send_from_directory, abort, Response,
                   stream_with_context)
from PIL import Image, ImageOps, ImageDraw, ImageFont

# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

with open("config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

TEMP_LOGO_DIR = os.path.join(tempfile.gettempdir(), "wm_logos")
os.makedirs(TEMP_LOGO_DIR, exist_ok=True)

VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}

# ─── FFmpeg ───────────────────────────────────────────────────────────────────
def get_ffmpeg():
    """Localiza o binario ffmpeg: imageio_ffmpeg primeiro, depois PATH."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return p
    raise RuntimeError(
        "FFmpeg nao encontrado. Instale via: pip install imageio-ffmpeg  "
        "ou baixe em ffmpeg.org"
    )

def probe_video(path, ffmpeg_bin):
    """Retorna dict com duration, width, height do video."""
    result = subprocess.run(
        [ffmpeg_bin, "-i", path, "-hide_banner"],
        capture_output=True, text=True, errors="replace"
    )
    out = result.stderr + result.stdout
    duration, width, height = 10.0, 1280, 720

    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", out)
    if m:
        h, mn, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        duration = h * 3600 + mn * 60 + s + cs / 100

    m = re.search(r"(\d{2,5})x(\d{2,5})(?:[,\s])", out)
    if m:
        width, height = int(m[1]), int(m[2])

    return {"duration": max(duration, 0.1), "width": width, "height": height}

# ─── Jobs (progresso em background) ──────────────────────────────────────────
JOBS: dict = {}
JOBS_LOCK = threading.Lock()

def job_create():
    jid = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[jid] = {"status": "pending", "progress": 0,
                     "message": "Aguardando...", "result": None,
                     "error": None, "created": time.time()}
    return jid

def job_update(jid, **kw):
    with JOBS_LOCK:
        j = JOBS.get(jid)
        if not j:
            return
        for k, v in kw.items():
            if k == "progress":
                j[k] = min(100, max(0, v))
            elif v is not None:
                j[k] = v

def job_get(jid):
    with JOBS_LOCK:
        return dict(JOBS.get(jid, {}))

def job_cleanup():
    cutoff = time.time() - 3600
    with JOBS_LOCK:
        stale = [jid for jid, j in JOBS.items() if j["created"] < cutoff]
        for jid in stale:
            j = JOBS.pop(jid, {})
            res = j.get("result")
            if res:
                try:
                    r = json.loads(res)
                    os.unlink(r["path"])
                except Exception:
                    pass

# ─── Helpers imagem ───────────────────────────────────────────────────────────
def _get_font(size):
    candidates = []
    if sys.platform == "win32":
        candidates = ["C:/Windows/Fonts/arialbd.ttf",
                      "C:/Windows/Fonts/arial.ttf",
                      "C:/Windows/Fonts/verdanab.ttf"]
    elif sys.platform == "darwin":
        candidates = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                      "/System/Library/Fonts/Helvetica.ttc"]
    else:
        candidates = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def hex_to_rgba(h, alpha=255):
    h = (h or "#ffffff").lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)

def apply_opacity(im, opacity):
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    a = im.split()[-1].point(lambda p: int(p * opacity))
    im.putalpha(a)
    return im

def place_logo(bw, bh, lw, lh, margin, position):
    cx, cy = (bw - lw) // 2, (bh - lh) // 2
    r, b, m = bw - lw - margin, bh - lh - margin, margin
    return {"top-left": (m, m), "top-center": (cx, m), "top-right": (r, m),
            "center": (cx, cy), "bottom-left": (m, b),
            "bottom-center": (cx, b), "bottom-right": (r, b)}.get(position, (r, b))

def text_to_wm_image(text, color, bg_color, bg_opacity, ref_size, scale_pct=15):
    """
    Gera imagem RGBA com o texto.
    O tamanho final da imagem ja corresponde ao tamanho real no output:
      altura_fonte = ref_size * scale_pct / 100 * 0.55
    Assim nao e preciso redimensionar depois — identico ao preview JS.
    """
    # Mesmo calculo que o canvas JS: ref * scale/100 * 0.55
    fs = max(12, int(ref_size * scale_pct / 100 * 0.55))
    font = _get_font(fs)
    dummy = Image.new("RGBA", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    px, py = max(4, fs // 4), max(2, fs // 6)
    w = (bbox[2] - bbox[0]) + px * 2
    h = (bbox[3] - bbox[1]) + py * 2
    bg_a = int((bg_opacity or 0) / 100 * 255)
    img = Image.new("RGBA", (max(w, 1), max(h, 1)),
                    hex_to_rgba(bg_color or "#000000", bg_a))
    ImageDraw.Draw(img).text((px, py), text, font=font,
                              fill=hex_to_rgba(color or "#ffffff"))
    img._is_text_wm = True  # flag para nao redimensionar nos processors
    return img

def process_image_pil(image_file, wm: Image.Image,
                      position, scale_pct, margin_pct, opacity_pct,
                      is_text=False) -> BytesIO:
    im = ImageOps.exif_transpose(Image.open(image_file)).convert("RGBA")
    bw, bh = im.size
    ref = min(bw, bh)
    if is_text:
        # Texto: ja esta no tamanho certo relativo ao ref_size do video/imagem
        # Apenas aplica opacidade, sem redimensionar
        lw, lh = wm.width, wm.height
        wm_r = apply_opacity(wm.copy(), opacity_pct / 100)
    else:
        lw = max(1, int(ref * scale_pct / 100))
        lh = max(1, int(lw / (wm.width / wm.height)))
        wm_r = apply_opacity(wm.resize((lw, lh), Image.LANCZOS), opacity_pct / 100)
    mg = int(ref * margin_pct / 100)
    x, y = place_logo(bw, bh, lw, lh, mg, position)
    out = im.copy()
    out.alpha_composite(wm_r, (x, y))
    buf = BytesIO()
    out.convert("RGBA").save(buf, "PNG", optimize=True)
    buf.seek(0)
    return buf

# ─── Video com FFmpeg ─────────────────────────────────────────────────────────
# Periodo de animacao em segundos (loop)
ANIM_PERIOD = 5.0

def _build_overlay_expr(vw, vh, lw, lh, margin, position, motion, period=ANIM_PERIOD):
    """
    Retorna string do filtro overlay para FFmpeg.
    Expressoes avaliadas por frame — 't' = tempo em segundos.
    """
    P = period
    sx, sy = place_logo(vw, vh, lw, lh, margin, position)

    if motion == "none":
        return f"overlay=x={sx}:y={sy}:format=auto"

    # helper: triangulo (0->1->0) suave com bounce
    # tri(t,P) = 1 - |2*mod(t,P)/P - 1|
    def tri_x():
        return f"(0-{lw})+({vw}+{lw})*(1-abs(2*mod(t\\,{P})/{P}-1))"
    def tri_y():
        return f"(0-{lh})+({vh}+{lh})*(1-abs(2*mod(t\\,{P*0.7:.2f})/{P*0.7:.2f}-1))"

    exprs = {
        "left-to-right": (
            f"(0-overlay_w)+mod(t\\,{P})*({vw}+overlay_w)/{P}",
            f"(main_h-overlay_h)/2"
        ),
        "right-to-left": (
            f"main_w-mod(t\\,{P})*({vw}+overlay_w)/{P}",
            f"(main_h-overlay_h)/2"
        ),
        "bottom-to-top": (
            f"(main_w-overlay_w)/2",
            f"main_h-mod(t\\,{P})*({vh}+overlay_h)/{P}"
        ),
        "top-to-bottom": (
            f"(main_w-overlay_w)/2",
            f"(0-overlay_h)+mod(t\\,{P})*({vh}+overlay_h)/{P}"
        ),
        "pendulum-x": (
            f"(main_w-overlay_w)/2+(main_w-overlay_w)/2*sin(mod(t\\,{P})*6.2832/{P})",
            f"(main_h-overlay_h)/2"
        ),
        "pendulum-y": (
            f"(main_w-overlay_w)/2",
            f"(main_h-overlay_h)/2+(main_h-overlay_h)/3*sin(mod(t\\,{P})*6.2832/{P})"
        ),
        "bounce-x": (
            f"({vw}+{lw})*(1-abs(2*mod(t\\,{P})/{P}-1))-{lw}",
            f"(main_h-overlay_h)/2"
        ),
        "bounce-y": (
            f"(main_w-overlay_w)/2",
            f"({vh}+{lh})*(1-abs(2*mod(t\\,{P})/{P}-1))-{lh}"
        ),
        "diagonal-bounce": (
            f"({vw}+{lw})*(1-abs(2*mod(t\\,{P})/{P}-1))-{lw}",
            f"({vh}+{lh})*(1-abs(2*mod(t\\,{P*0.7:.3f})/{P*0.7:.3f}-1))-{lh}"
        ),
        "diagonal-linear": (
            f"(0-{lw})+mod(t\\,{P})*({vw}+{lw})/{P}",
            f"(0-{lh})+mod(t\\,{P})*({vh}+{lh})/{P}"
        ),
    }
    xe, ye = exprs.get(motion, (str(sx), str(sy)))
    return f"overlay=x='{xe}':y='{ye}':format=auto"


def process_video_ffmpeg(video_path, wm: Image.Image,
                         position, scale_pct, margin_pct, opacity_pct,
                         motion, progress_cb=None,
                         endscreen_path=None, endscreen_duration=5):
    """
    Aplica marca d'agua no video usando FFmpeg diretamente.
    Retorna caminho do arquivo de saida (mp4).
    """
    ffmpeg = get_ffmpeg()

    if progress_cb:
        progress_cb(4, "Analisando video...")

    info = probe_video(video_path, ffmpeg)
    vw, vh, dur = info["width"], info["height"], info["duration"]

    if progress_cb:
        progress_cb(8, "Preparando...")

    # Arquivo de saida
    fd_out, out_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd_out)
    wm_path = None

    if wm is not None:
        # Redimensiona e aplica opacidade na marca d'agua
        ref = min(vw, vh)
        is_text = getattr(wm, "_is_text_wm", False)
        if is_text:
            lw, lh = wm.width, wm.height
            wm_r = apply_opacity(wm.copy(), opacity_pct / 100)
        else:
            lw = max(1, int(ref * scale_pct / 100))
            lh = max(1, int(lw / (wm.width / wm.height)))
            wm_r = apply_opacity(wm.resize((lw, lh), Image.LANCZOS), opacity_pct / 100)
        mg = int(ref * margin_pct / 100)

        fd_wm, wm_path = tempfile.mkstemp(suffix=".png")
        os.close(fd_wm)
        wm_r.save(wm_path, "PNG")

        overlay = _build_overlay_expr(vw, vh, lw, lh, mg, position, motion)

        cmd = [
            ffmpeg, "-y", "-hide_banner",
            "-i", video_path,
            "-i", wm_path,
            "-filter_complex", f"[0:v][1:v]{overlay},format=yuv420p",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-profile:v", "high",
            "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-threads", "0",
            out_path,
        ]
    else:
        # Sem watermark: re-encode para formato padrao (necessario para concat)
        cmd = [
            ffmpeg, "-y", "-hide_banner",
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-profile:v", "high",
            "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-threads", "0",
            out_path,
        ]

    if progress_cb:
        progress_cb(12, f"Codificando {dur:.0f}s de video (ultrafast)...")

    # Lanca processo FFmpeg; lê stderr em thread separada
    proc = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        text=True,
        errors="replace",
    )

    # Thread que le stderr e atualiza progresso
    time_re = re.compile(r"time=(\d+):(\d+):(\d+)\.(\d+)")
    encoded_sec = [0.0]

    def _read_stderr():
        buf = ""
        for chunk in iter(lambda: proc.stderr.read(256), ""):
            buf += chunk
            m = time_re.search(buf)
            if m:
                h, mn, s, cs = int(m[1]), int(m[2]), int(m[3]), int(m[4])
                encoded_sec[0] = h * 3600 + mn * 60 + s + cs / 100
            buf = buf[-300:]  # mantém buffer pequeno

    t_err = threading.Thread(target=_read_stderr, daemon=True)
    t_err.start()

    # Polling de progresso enquanto ffmpeg roda
    while proc.poll() is None:
        enc = encoded_sec[0]
        if dur > 0 and progress_cb:
            pct = 12 + int(80 * min(1.0, enc / dur))
            progress_cb(pct, f"Codificando... {enc:.1f}s / {dur:.1f}s")
        time.sleep(0.4)

    t_err.join(timeout=2)

    # Limpa watermark temp
    if wm_path:
        try:
            os.unlink(wm_path)
        except Exception:
            pass

    if proc.returncode != 0:
        try:
            os.unlink(out_path)
        except Exception:
            pass
        raise RuntimeError(f"FFmpeg retornou codigo {proc.returncode}")

    if progress_cb:
        progress_cb(94, "Finalizando...")

    # ── Tela final: concatena imagem como segmento no final do video ──
    if endscreen_path and os.path.exists(endscreen_path):
        if progress_cb:
            progress_cb(95, "Adicionando tela final...")

        # Gera segmento de video a partir da imagem, com mesma resolucao e audio silencioso
        fd_es, es_vid = tempfile.mkstemp(suffix=".mp4")
        os.close(fd_es)
        es_cmd = [
            ffmpeg, "-y", "-hide_banner",
            "-loop", "1", "-i", endscreen_path,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(endscreen_duration),
            "-vf", f"scale={vw}:{vh}:force_original_aspect_ratio=decrease,"
                   f"pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p", "-shortest",
            es_vid,
        ]
        r = subprocess.run(es_cmd, capture_output=True, text=True, errors="replace")
        if r.returncode != 0:
            try: os.unlink(es_vid)
            except: pass
        else:
            # Concatena via concat demuxer
            fd_lst, lst_path = tempfile.mkstemp(suffix=".txt")
            os.close(fd_lst)
            with open(lst_path, "w") as lf:
                lf.write(f"file '{out_path}'\nfile '{es_vid}'\n")
            fd_final, final_path = tempfile.mkstemp(suffix=".mp4")
            os.close(fd_final)
            cat_cmd = [
                ffmpeg, "-y", "-hide_banner",
                "-f", "concat", "-safe", "0", "-i", lst_path,
                "-c", "copy",
                "-movflags", "+faststart",
                final_path,
            ]
            rc = subprocess.run(cat_cmd, capture_output=True, text=True, errors="replace")
            # Limpa temporarios
            for p in [lst_path, es_vid]:
                try: os.unlink(p)
                except: pass
            if rc.returncode == 0:
                try: os.unlink(out_path)
                except: pass
                out_path = final_path
            else:
                try: os.unlink(final_path)
                except: pass

    return out_path


# ─── Resolucao de marca d'agua ────────────────────────────────────────────────
def logo_from_token(token):
    matches = [f for f in os.listdir(TEMP_LOGO_DIR) if f.startswith(token)]
    if not matches:
        raise FileNotFoundError("Token de logo invalido ou expirado.")
    return Image.open(os.path.join(TEMP_LOGO_DIR, matches[0])).convert("RGBA")

def logo_from_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "WatermarkTool/3.1"})
    with urllib.request.urlopen(req, timeout=12) as r:
        data = r.read()
    return Image.open(BytesIO(data)).convert("RGBA")

def resolve_watermark(form, files_dict, ref_size=500, scale_pct=15):
    wm_type = (form.get("wm_type") or "image").strip()
    if wm_type == "text":
        text = (form.get("wm_text") or "").strip()
        if not text:
            raise ValueError("Digite o texto da marca d'agua.")
        return text_to_wm_image(
            text,
            form.get("wm_color", "#ffffff"),
            form.get("wm_bg_color", "#000000"),
            int(form.get("wm_bg_opacity", 0) or 0),
            ref_size,
            scale_pct,
        )
    f = files_dict.get("logo_file_inline")
    if f and f.filename:
        return Image.open(f).convert("RGBA")
    token = (form.get("logo_token") or "").strip()
    if token:
        return logo_from_token(token)
    url = (form.get("logo_url") or "").strip()
    if url:
        return logo_from_url(url)
    raise ValueError("Nenhuma logo fornecida.")

def get_params(form):
    return (
        form.get("position") or CFG["default_position"],
        float(form.get("scale_pct")   or CFG["default_scale_pct"]),
        float(form.get("margin_pct")  or CFG["default_margin_pct"]),
        float(form.get("opacity_pct") or CFG["default_opacity_pct"]),
    )

def file_ext(name):
    return os.path.splitext(name or "")[1].lower()


# ─── Job runner ───────────────────────────────────────────────────────────────
def run_job(jid, tmp_files, watermark, position, scale_pct,
            margin_pct, opacity_pct, motion,
            endscreen_path=None, endscreen_duration=5):
    """Processa todos os arquivos em background."""
    try:
        job_update(jid, status="running", progress=2, message="Iniciando...")
        total = len(tmp_files)
        results = []

        for idx, (orig_name, tmp_path) in enumerate(tmp_files):
            ext  = file_ext(orig_name)
            base = orig_name.rsplit(".", 1)[0]
            bp   = int(idx / total * 100)
            fp   = int((idx + 1) / total * 100)

            def cb(pct, msg, _bp=bp, _fp=fp):
                combined = _bp + int(pct / 100 * (_fp - _bp))
                label = f"[{idx+1}/{total}] {msg}" if total > 1 else msg
                job_update(jid, progress=combined, message=label)

            cb(1, f"Processando {orig_name}...")

            if ext in VIDEO_EXTS:
                out = process_video_ffmpeg(
                    tmp_path, watermark, position,
                    scale_pct, margin_pct, opacity_pct, motion, cb,
                    endscreen_path=endscreen_path,
                    endscreen_duration=endscreen_duration
                )
                results.append((f"{base}_watermark.mp4", out))
            else:
                if watermark is None:
                    # Sem watermark em imagem — pula
                    results.append((f"{base}.png", tmp_path))
                    continue
                buf = process_image_pil(tmp_path, watermark, position,
                                        scale_pct, margin_pct, opacity_pct,
                                        is_text=getattr(watermark, "_is_text_wm", False))
                fd, out = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                with open(out, "wb") as fh:
                    fh.write(buf.getvalue())
                results.append((f"{base}_watermark.png", out))

            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        job_update(jid, progress=97, message="Empacotando resultado...")

        if len(results) == 1:
            name, path = results[0]
            job_update(jid, status="done", progress=100, message="Pronto!",
                       result=json.dumps({"path": path, "name": name}))
        else:
            stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            fd_z, zip_path = tempfile.mkstemp(suffix=".zip")
            os.close(fd_z)
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, path in results:
                    zf.write(path, name)
                    try:
                        os.unlink(path)
                    except Exception:
                        pass
            job_update(jid, status="done", progress=100, message="Pronto!",
                       result=json.dumps({
                           "path": zip_path,
                           "name": f"watermarked_{stamp}.zip"
                       }))

    except Exception as e:
        job_update(jid, status="error", message=f"Erro: {e}", error=str(e))
        for _, tp in (tmp_files or []):
            try:
                os.unlink(tp)
            except Exception:
                pass


# ─── Rotas API ────────────────────────────────────────────────────────────────
@app.post("/api/process")
def api_process():
    job_cleanup()
    position, scale_pct, margin_pct, opacity_pct = get_params(request.form)
    motion = request.form.get("wm_motion", "none")

    all_files = [f for f in request.files.getlist("images") if f.filename]
    if not all_files:
        return jsonify(error="Envie ao menos um arquivo."), 400

    # Salva em temp primeiro para poder provar dimensoes de qualquer tipo
    tmp_files = []
    for f in all_files:
        ext = file_ext(f.filename) or ".bin"
        fd, tp = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        f.save(tp)
        tmp_files.append((f.filename, tp))

    # Descobre ref_size real (imagem ou video)
    ref_size = 500
    try:
        ffb = get_ffmpeg()
    except Exception:
        ffb = None
    for orig_name, tp in tmp_files:
        ext = file_ext(orig_name)
        try:
            if ext in IMAGE_EXTS:
                ref_size = min(Image.open(tp).size)
                break
            elif ext in VIDEO_EXTS and ffb:
                info = probe_video(tp, ffb)
                ref_size = min(info["width"], info["height"])
                break
        except Exception:
            pass

    # ── Tela final (endscreen) ──
    endscreen_path = None
    endscreen_duration = int(request.form.get("endscreen_duration", 0) or 0)
    es_file = request.files.get("endscreen_file")
    es_token = (request.form.get("endscreen_token") or "").strip()
    if es_file and es_file.filename and endscreen_duration > 0:
        fd_es, endscreen_path = tempfile.mkstemp(suffix=os.path.splitext(es_file.filename)[1].lower() or ".png")
        os.close(fd_es)
        es_file.save(endscreen_path)
    elif es_token and endscreen_duration > 0:
        matches = [f for f in os.listdir(TEMP_LOGO_DIR) if f.startswith(es_token)]
        if matches:
            endscreen_path = os.path.join(TEMP_LOGO_DIR, matches[0])

    wm = None
    try:
        wm = resolve_watermark(request.form, request.files, ref_size, scale_pct)
    except Exception:
        pass  # watermark e opcional se tiver endscreen

    if wm is None and not endscreen_path:
        for _, tp in tmp_files:
            try: os.unlink(tp)
            except Exception: pass
        return jsonify(error="Envie uma marca d'agua ou uma tela final."), 400

    jid = job_create()
    threading.Thread(
        target=run_job,
        args=(jid, tmp_files, wm, position, scale_pct, margin_pct, opacity_pct, motion),
        kwargs={"endscreen_path": endscreen_path, "endscreen_duration": endscreen_duration},
        daemon=True,
    ).start()

    return jsonify(job_id=jid)


@app.get("/api/progress/<jid>")
def api_progress(jid):
    def stream():
        last = -1
        deadline = time.time() + 600
        while time.time() < deadline:
            j = job_get(jid)
            if not j:
                yield 'data: {"status":"error","message":"Job nao encontrado"}\n\n'
                return
            payload = json.dumps({
                "status":   j.get("status", "pending"),
                "progress": j.get("progress", 0),
                "message":  j.get("message", ""),
                "error":    j.get("error"),
            })
            if j.get("progress") != last or j.get("status") in ("done", "error"):
                last = j.get("progress")
                yield f"data: {payload}\n\n"
            if j.get("status") in ("done", "error"):
                return
            time.sleep(0.35)

    resp = Response(stream_with_context(stream()), mimetype="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


@app.get("/api/download/<jid>")
def api_download(jid):
    j = job_get(jid)
    if not j or j.get("status") != "done":
        abort(404)
    res  = json.loads(j["result"])
    path = res["path"]
    name = res["name"]
    if not os.path.exists(path):
        abort(410)
    mime = ("video/mp4"       if name.endswith(".mp4") else
            "application/zip" if name.endswith(".zip") else "image/png")
    return send_file(path, as_attachment=True, download_name=name, mimetype=mime)


# ─── Rotas principais ─────────────────────────────────────────────────────────
@app.get("/")
def index():
    return render_template("index.html", cfg=CFG)

@app.get("/guebly")
def guebly_panel():
    return render_template("guebly.html", cfg=CFG,
                            companies=CFG.get("guebly_companies", []))

@app.post("/guebly/process")
def guebly_process():
    companies  = {c["id"]: c for c in CFG.get("guebly_companies", [])}
    company_id = (request.form.get("company_id") or "").strip()
    if company_id not in companies:
        abort(400, "Empresa nao encontrada.")
    company = companies[company_id]
    position, scale_pct, margin_pct, opacity_pct = get_params(request.form)
    try:
        wm = resolve_watermark(request.form, request.files)
    except ValueError:
        src   = company.get("logo_url", "")
        token = company.get("logo_token", "")
        if token:
            try:
                wm = logo_from_token(token)
            except FileNotFoundError:
                abort(400, f"Logo de '{company['name']}' nao encontrada.")
        elif src:
            try:
                wm = logo_from_url(src)
            except Exception as e:
                abort(400, f"Erro ao carregar logo: {e}")
        else:
            abort(400, f"'{company['name']}' sem logo configurada.")
    except Exception as e:
        abort(400, f"Erro: {e}")

    files = [f for f in request.files.getlist("images") if f.filename]
    if not files:
        abort(400, "Envie ao menos um arquivo.")

    if len(files) == 1:
        f    = files[0]
        ext  = file_ext(f.filename)
        base = f.filename.rsplit(".", 1)[0]
        if ext in VIDEO_EXTS:
            fd_in, ti = tempfile.mkstemp(suffix=ext)
            os.close(fd_in)
            f.save(ti)
            out = process_video_ffmpeg(ti, wm, position, scale_pct, margin_pct, opacity_pct, "none")
            try: os.unlink(ti)
            except Exception: pass
            return send_file(out, as_attachment=True,
                             download_name=f"{base}_watermark.mp4", mimetype="video/mp4")
        buf = process_image_pil(f, wm, position, scale_pct, margin_pct, opacity_pct,
                                 is_text=getattr(wm, "_is_text_wm", False))
        return send_file(buf, as_attachment=True,
                         download_name=f"{base}_watermark.png", mimetype="image/png")

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            ext  = file_ext(f.filename)
            base = f.filename.rsplit(".", 1)[0]
            try:
                if ext in VIDEO_EXTS:
                    fd_in, ti = tempfile.mkstemp(suffix=ext)
                    os.close(fd_in)
                    f.save(ti)
                    out = process_video_ffmpeg(ti, wm, position, scale_pct, margin_pct, opacity_pct, "none")
                    with open(out, "rb") as fh:
                        zf.writestr(f"{base}_watermark.mp4", fh.read())
                    for p in (ti, out):
                        try: os.unlink(p)
                        except Exception: pass
                else:
                    buf = process_image_pil(f, wm, position, scale_pct, margin_pct, opacity_pct,
                                             is_text=getattr(wm, "_is_text_wm", False))
                    zf.writestr(f"{base}_watermark.png", buf.getvalue())
            except Exception as e:
                zf.writestr(f"ERRO_{f.filename}.txt", str(e))
    zip_buf.seek(0)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    return send_file(zip_buf, as_attachment=True,
                     download_name=f"watermarked_{stamp}.zip",
                     mimetype="application/zip")


# ─── Upload logo temp ─────────────────────────────────────────────────────────
@app.post("/upload-logo")
def upload_logo():
    f = request.files.get("logo_file")
    if not f:
        return jsonify(error="Nenhum arquivo enviado"), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        return jsonify(error="Use PNG, JPG ou WEBP."), 400
    token = uuid.uuid4().hex
    f.save(os.path.join(TEMP_LOGO_DIR, f"{token}{ext}"))
    return jsonify(token=token, ext=ext, preview_url=f"/temp-logo/{token}{ext}")

@app.get("/temp-logo/<filename>")
def temp_logo(filename):
    if ".." in filename or "/" in filename:
        abort(404)
    return send_from_directory(TEMP_LOGO_DIR, filename)


# ─── Start ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  WatermarkTool v3.1 - http://localhost:{port}")
    print(f"  Painel interno  - http://localhost:{port}/guebly\n")
    app.run(host="0.0.0.0", port=port, debug=True)
