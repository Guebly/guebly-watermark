@echo off
echo ============================================
echo   Instalando dependencias - Marca d'agua
echo ============================================
echo.

py -m pip install flask pillow

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Tentando com python...
    python -m pip install flask pillow
)

echo.
echo ============================================
echo   Pronto! Agora rode o arquivo iniciar.bat
echo ============================================
pause
