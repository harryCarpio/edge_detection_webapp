@echo off
REM Script para iniciar la aplicación Flask en Windows

echo.
echo ========================================
echo    Canny Edge Detection - Flask App
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Descarga Python desde: https://www.python.org/
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo OK
)

REM Activar entorno virtual
echo [2/3] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo OK

REM Instalar dependencias
echo [3/3] Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    echo.
    echo Intenta ejecutar manualmente:
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo OK

REM Iniciar la aplicación
echo.
echo Iniciando aplicación...
echo.
echo ========================================
echo APLICACION EN EJECUCION
echo Accede a: http://localhost:5000
echo Presiona Ctrl+C para detener
echo ========================================
echo.

python app.py

pause
