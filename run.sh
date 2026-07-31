#!/usr/bin/env bash
set -e
VENV_DIR="$HOME/.venvs/ecomarket"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] No se encontro Python 3 instalado."
    echo "Instalalo desde https://www.python.org/downloads/ y vuelve a ejecutar este script."
    exit 1
fi

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creando entorno virtual en $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
fi

echo "Instalando dependencias, puede tardar varios minutos la primera vez..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV_DIR/bin/python" -m pip install -r "$DIR/requirements.txt"

if [ ! -f "$DIR/opiniones.csv" ]; then
    echo "Generando dataset de opiniones de ejemplo..."
    "$VENV_DIR/bin/python" "$DIR/generar_dataset.py"
fi

echo ""
echo "Iniciando EcoMarket en http://127.0.0.1:5000  (Ctrl+C para detener)"
echo "Nota: la primera vez que analices una opinion se descargara un modelo de IA (~500MB desde internet)."
echo ""
"$VENV_DIR/bin/python" "$DIR/app.py"
