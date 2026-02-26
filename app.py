"""
WatermarkTool — aplicador de marca d'água via Flask + Pillow
============================================================
Rotas públicas:
  GET  /           → ferramenta geral (upload/URL da logo)
  POST /process    → processa e devolve PNG ou ZIP

Rota interna (não divulgada):
  GET  /guebly          → painel Guebly com empresas pré-configuradas
  POST /guebly/process  → processa usando a logo da empresa selecionada

Utilitários:
  POST /upload-logo         → faz upload temporário da logo, devolve token
  GET  /temp-logo/<arquivo> → serve logo temporária para preview
"""

from io import BytesIO
import os, json, datetime, zipfile, uuid, tempfile, urllib.request
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory, abort

from PIL import Image, ImageOps

# ─────────────────────────────────────────────
# Inicialização
# ─────────────────────────────────────────────
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB

with open("config.json", "r", encoding="utf-8") as f:
    CFG = json.load(f)

# Logos temporárias ficam em pasta do sistema operacional
TEMP_LOGO_DIR = os.path.join(tempfile.gettempdir(), "wm_logos")
os.makedirs(TEMP_LOGO_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# Helpers de imagem
# ─────────────────────────────────────────────
def apply_opacity(im: Image.Image, opacity: float) -> Image.Image:
    """Aplica opacidade (0.0–1.0) ao canal alpha da imagem."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    alpha = im.split()[-1]
    alpha = alpha.point(lambda p: int(p * opacity))
    im.putalpha(alpha)
    return im


def place_logo(base_w, base_h, logo_w, logo_h, margin, position):
    """Retorna coordenadas (x, y) para posicionar a logo."""
    cx = (base_w - logo_w) // 2
    cy = (base_h - logo_h) // 2
    r  = base_w - logo_w - margin
    b  = base_h - logo_h - margin
    m  = margin
    return {
        "top-left":      (m,  m),
        "top-center":    (cx, m),
        "top-right":     (r,  m),
        "center":        (cx, cy),
        "bottom-left":   (m,  b),
        "bottom-center": (cx, b),
        "bottom-right":  (r,  b),
    }.get(position, (r, b))


def process_image(image_file, logo: Image.Image, position, scale_pct, margin_pct, opacity_pct) -> BytesIO:
    """Abre a imagem, redimensiona e compõe a logo, devolve buffer PNG."""
    im = Image.open(image_file)
    im = ImageOps.exif_transpose(im).convert("RGBA")
    base_w, base_h = im.size
    base_ref = min(base_w, base_h)

    # Escala da logo relativa à menor dimensão da imagem base
    target_w = max(1, int(base_ref * (scale_pct / 100.0)))
    aspect   = logo.width / logo.height
    logo_w   = target_w
    logo_h   = max(1, int(target_w / aspect))

    resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
    resized = apply_opacity(resized, opacity_pct / 100.0)

    margin = int(base_ref * (margin_pct / 100.0))
    x, y   = place_logo(base_w, base_h, logo_w, logo_h, margin, position)

    out = im.copy()
    out.alpha_composite(resized, (x, y))

    buff = BytesIO()
    out.convert("RGBA").save(buff, format="PNG", optimize=True)
    buff.seek(0)
    return buff


def logo_from_token(token: str) -> Image.Image:
    """Carrega logo a partir de token de upload temporário."""
    matches = [fn for fn in os.listdir(TEMP_LOGO_DIR) if fn.startswith(token)]
    if not matches:
        raise FileNotFoundError("Token de logo inválido ou expirado.")
    return Image.open(os.path.join(TEMP_LOGO_DIR, matches[0])).convert("RGBA")


def logo_from_url(url: str) -> Image.Image:
    """Baixa logo a partir de URL pública."""
    req = urllib.request.Request(url, headers={"User-Agent": "WatermarkTool/2.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = resp.read()
    return Image.open(BytesIO(data)).convert("RGBA")


def resolve_logo(form, files_dict) -> Image.Image:
    """
    Resolve a logo de acordo com prioridade:
      1. Arquivo enviado diretamente no form (logo_file_inline)
      2. Token de upload prévio (logo_token)
      3. URL externa (logo_url)
    """
    f = files_dict.get("logo_file_inline")
    if f and f.filename:
        return Image.open(f).convert("RGBA")

    token = form.get("logo_token", "").strip()
    if token:
        return logo_from_token(token)

    url = form.get("logo_url", "").strip()
    if url:
        return logo_from_url(url)

    raise ValueError("Nenhuma logo fornecida. Envie um arquivo ou URL.")


def build_response(files, logo_img, position, scale_pct, margin_pct, opacity_pct):
    """Processa lista de imagens e devolve PNG (1 arquivo) ou ZIP (múltiplos)."""
    files = [f for f in files if f.filename]
    if not files:
        abort(400, "Envie ao menos uma imagem.")

    if len(files) == 1:
        buff = process_image(files[0], logo_img, position, scale_pct, margin_pct, opacity_pct)
        base = (files[0].filename or "imagem").rsplit(".", 1)[0]
        return send_file(buff, as_attachment=True,
                         download_name=f"{base}_watermark.png",
                         mimetype="image/png")

    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            try:
                buff = process_image(f, logo_img, position, scale_pct, margin_pct, opacity_pct)
                base = (f.filename or "img").rsplit(".", 1)[0]
                zf.writestr(f"{base}_watermark.png", buff.getvalue())
            except Exception as e:
                zf.writestr(f"ERRO_{f.filename or 'file'}.txt", str(e))
    zip_buf.seek(0)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    return send_file(zip_buf, as_attachment=True,
                     download_name=f"watermarked_{stamp}.zip",
                     mimetype="application/zip")


def get_params(form):
    """Extrai parâmetros de marca d'água do form com fallback para config."""
    return (
        form.get("position")  or CFG["default_position"],
        float(form.get("scale_pct")   or CFG["default_scale_pct"]),
        float(form.get("margin_pct")  or CFG["default_margin_pct"]),
        float(form.get("opacity_pct") or CFG["default_opacity_pct"]),
    )


# ─────────────────────────────────────────────
# Rotas — Ferramenta pública
# ─────────────────────────────────────────────
@app.get("/")
def index():
    return render_template("index.html", cfg=CFG)


@app.post("/process")
def process():
    try:
        logo_img = resolve_logo(request.form, request.files)
    except (FileNotFoundError, ValueError) as e:
        abort(400, str(e))
    except Exception as e:
        abort(400, f"Erro ao carregar logo: {e}")

    position, scale_pct, margin_pct, opacity_pct = get_params(request.form)
    return build_response(request.files.getlist("images"),
                          logo_img, position, scale_pct, margin_pct, opacity_pct)


# ─────────────────────────────────────────────
# Rotas — Painel interno Guebly  (/guebly)
# ─────────────────────────────────────────────
@app.get("/guebly")
def guebly_panel():
    companies = CFG.get("guebly_companies", [])
    return render_template("guebly.html", cfg=CFG, companies=companies)


@app.post("/guebly/process")
def guebly_process():
    companies = {c["id"]: c for c in CFG.get("guebly_companies", [])}
    company_id = request.form.get("company_id", "").strip()

    if company_id not in companies:
        abort(400, "Empresa não encontrada.")

    company = companies[company_id]

    # A logo pode ter sido sobrescrita manualmente na sessão (upload/URL)
    try:
        logo_img = resolve_logo(request.form, request.files)
    except ValueError:
        # Sem sobrescrita: usa a logo da empresa configurada
        logo_source = company.get("logo_url", "")
        logo_token  = company.get("logo_token", "")

        if logo_token:
            try:
                logo_img = logo_from_token(logo_token)
            except FileNotFoundError:
                abort(400, f"Logo da empresa '{company['name']}' não encontrada. Reconfigure em config.json.")
        elif logo_source:
            try:
                logo_img = logo_from_url(logo_source)
            except Exception as e:
                abort(400, f"Erro ao carregar logo da URL configurada: {e}")
        else:
            abort(400, f"A empresa '{company['name']}' não tem logo configurada.")
    except Exception as e:
        abort(400, f"Erro ao carregar logo: {e}")

    position, scale_pct, margin_pct, opacity_pct = get_params(request.form)
    return build_response(request.files.getlist("images"),
                          logo_img, position, scale_pct, margin_pct, opacity_pct)


# ─────────────────────────────────────────────
# Rotas — Upload temporário de logo
# ─────────────────────────────────────────────
@app.post("/upload-logo")
def upload_logo():
    f = request.files.get("logo_file")
    if not f:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        return jsonify({"error": "Formato inválido. Use PNG, JPG ou WEBP."}), 400

    token = uuid.uuid4().hex
    dest  = os.path.join(TEMP_LOGO_DIR, f"{token}{ext}")
    f.save(dest)

    return jsonify({
        "token":       token,
        "ext":         ext,
        "preview_url": f"/temp-logo/{token}{ext}",
    })


@app.get("/temp-logo/<filename>")
def temp_logo(filename):
    if ".." in filename or "/" in filename:
        abort(404)
    return send_from_directory(TEMP_LOGO_DIR, filename)


# ─────────────────────────────────────────────
# Inicialização
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  🚀  WatermarkTool rodando em http://localhost:{port}")
    print(f"  🔒  Painel interno em   http://localhost:{port}/guebly\n")
    app.run(host="0.0.0.0", port=port, debug=True)
