@echo off
echo.
echo  ============================================
echo    WatermarkTool v3.0 - Guebly Holding
echo  ============================================
echo.

cd /d "%~dp0"

py -m pip show flask >nul 2>&1
if %errorlevel% neq 0 goto INSTALL
py -m pip show moviepy >nul 2>&1
if %errorlevel% neq 0 goto INSTALL
goto START

:INSTALL
echo  Instalando dependencias (apenas na primeira vez)...
echo.
py -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    python -m pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo.
        echo  [ERRO] Falha ao instalar dependencias.
        echo  Verifique se o Python 3.9+ esta instalado.
        pause
        exit /b 1
    )
)
echo.
echo  Dependencias instaladas!
echo.

:START
echo  Iniciando servidor...
echo  Acesse: http://localhost:5000
echo  Painel: http://localhost:5000/guebly
echo.
echo  Para encerrar: feche essa janela ou Ctrl+C
echo.

py app.py
if %errorlevel% neq 0 (
    python app.py
)

echo.
pause
