@echo off
setlocal
set VENV_DIR=%USERPROFILE%\.venvs\ecomarket

where py >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro Python instalado.
    echo Descargalo desde https://www.python.org/downloads/ ^(marca "Add python.exe to PATH"^) y vuelve a ejecutar este script.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creando entorno virtual en %VENV_DIR% ...
    py -3 -m venv "%VENV_DIR%"
)

echo Instalando dependencias, puede tardar varios minutos la primera vez...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip >nul
"%VENV_DIR%\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias. Revisa el mensaje de arriba.
    pause
    exit /b 1
)

if not exist "%~dp0opiniones.csv" (
    echo Generando dataset de opiniones de ejemplo...
    "%VENV_DIR%\Scripts\python.exe" "%~dp0generar_dataset.py"
)

echo.
echo Iniciando EcoMarket en http://127.0.0.1:5000  (Ctrl+C para detener)
echo Nota: la primera vez que analices una opinion se descargara un modelo de IA (~500MB desde internet).
echo.
"%VENV_DIR%\Scripts\python.exe" "%~dp0app.py"
endlocal
