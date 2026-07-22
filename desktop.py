"""Guebly Watermark — aplicativo de desktop.

Sobe o servidor Flask numa porta livre e abre uma janela nativa (pywebview),
sem depender do navegador. É este arquivo que o PyInstaller empacota no .exe.

Por que pywebview e não Electron: o app é Python/Flask e já traz o FFmpeg
(imageio-ffmpeg). Com Electron seria preciso empacotar Node + Python + FFmpeg
(~300 MB, três runtimes). Com pywebview o .exe usa o WebView2 que já existe no
Windows 10/11 — some um runtime inteiro e o instalador fica bem menor.
"""
import os
import socket
import sys
import threading
import time

# Quando roda dentro do .exe, os arquivos ficam na pasta temporária do PyInstaller.
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
sys.path.insert(0, BASE)

# O Windows agrupa janelas pelo AppUserModelID. Sem definir um proprio, o app
# herda o do interpretador Python e a barra de tarefas mostra o icone errado.
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "Guebly.Watermark")
    except Exception:
        pass

import webview  # noqa: E402
from app import app  # noqa: E402


def porta_livre() -> int:
    """Pede uma porta livre ao SO — evita conflito se algo já usa a 5000."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def espera_subir(porta: int, timeout: float = 20.0) -> bool:
    """Só abre a janela quando o servidor estiver de pé (evita tela em branco)."""
    fim = time.time() + timeout
    while time.time() < fim:
        try:
            with socket.create_connection(("127.0.0.1", porta), timeout=0.4):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def _icone_janela(caminho: str) -> None:
    """Aplica o icone na janela ja criada.

    O pywebview no Windows nao repassa o parametro `icon` para o WebView2, entao
    a janela ficava com o icone padrao mesmo com o .ico embutido no .exe.
    """
    try:
        import ctypes
        u, IMAGE_ICON, LR = ctypes.windll.user32, 1, 0x00000010
        hwnd = u.GetActiveWindow()
        for wparam, tam in ((1, 32), (0, 16)):      # ICON_BIG, ICON_SMALL
            h = u.LoadImageW(None, caminho, IMAGE_ICON, tam, tam, LR)
            if h:
                u.SendMessageW(hwnd, 0x0080, wparam, h)   # WM_SETICON
    except Exception:
        pass


def main() -> None:
    porta = porta_livre()

    def servidor() -> None:
        app.run(host="127.0.0.1", port=porta, debug=False,
                use_reloader=False, threaded=True)

    threading.Thread(target=servidor, daemon=True).start()

    if not espera_subir(porta):
        print("O servidor interno não subiu a tempo.", file=sys.stderr)
        sys.exit(1)

    icone = os.path.join(BASE, "static", "img", "app.ico")
    webview.create_window(
        "Guebly Watermark",
        f"http://127.0.0.1:{porta}/",
        width=1280,
        height=860,
        min_size=(980, 660),
        background_color="#0f1115",
    )
    if os.path.exists(icone):
        webview.windows[0].events.shown += lambda: _icone_janela(icone)
    webview.start(icon=icone if os.path.exists(icone) else None)


if __name__ == "__main__":
    main()
