#!/bin/bash
# Script para iniciar la aplicación Flask en Linux/macOS

echo ""
echo "========================================"
echo "   Canny Edge Detection - Flask App"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo "Instala Python desde: https://www.python.org/"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[1/3] Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el entorno virtual"
        exit 1
    fi
    echo "OK"
fi

# Activar entorno virtual
echo "[2/3] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo activar el entorno virtual"
    exit 1
fi
echo "OK"

# Instalar dependencias
echo "[3/3] Instalando dependencias..."
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi
echo "OK"

# Iniciar la aplicación
echo ""
echo "Iniciando aplicación..."
echo ""
echo "========================================"
echo "APLICACION EN EJECUCION"
echo "Accede a: http://localhost:5000"
echo "Presiona Ctrl+C para detener"
echo "========================================"
echo ""

python app.py
