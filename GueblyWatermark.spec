# PyInstaller — gera o GueblyWatermark.exe (um arquivo só)
#   pyinstaller GueblyWatermark.spec --noconfirm
#
# Empacota junto: templates, static (logos + ícone), config.json, VERSION e o
# binário do FFmpeg que vem no imageio-ffmpeg — assim o .exe roda sozinho,
# sem exigir Python nem FFmpeg instalados na máquina.
import os
from PyInstaller.utils.hooks import collect_data_files

dados = [
    ("templates", "templates"),
    ("static", "static"),
    ("config.json", "."),
    ("VERSION", "."),
]
# FFmpeg embutido
dados += collect_data_files("imageio_ffmpeg", include_py_files=False)

a = Analysis(
    ["desktop.py"],
    pathex=[],
    binaries=[],
    datas=dados,
    hiddenimports=["webview", "webview.platforms.edgechromium", "clr_loader"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GueblyWatermark",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               # sem janela preta de terminal
    disable_windowed_traceback=False,
    icon="static/img/app.ico",
)
