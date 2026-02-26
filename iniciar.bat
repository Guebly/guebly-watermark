@echo off
echo ============================================
echo   Marca d'agua - Guebly Holding
echo ============================================
echo.
echo Iniciando servidor...
echo Acesse: http://localhost:5000
echo.
echo Para encerrar: feche essa janela ou Ctrl+C
echo.

cd /d "%~dp0"

py app.py

if %errorlevel% neq 0 (
    python app.py
)

pause
