---
title: EcoMarket
emoji: 🌱
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# EcoMarket

Proyecto Final de Lenguaje de Programación para IA. Tienda ecológica hecha con Flask que permite:

- Registrar y listar productos (catálogo con SQLite).
- Analizar el sentimiento (positivo / negativo / neutral) de una opinión escrita, usando un modelo de IA en español (BETO) + un clasificador SVM entrenado con un dataset propio.

## Requisitos

- **Python 3.10 o superior** ([descargar aquí](https://www.python.org/downloads/); en Windows marca la casilla "Add python.exe to PATH" al instalar).
- Conexión a internet la **primera vez** que se analiza una opinión (se descarga el modelo `dccuchile/bert-base-spanish-wwm-cased`, ~500 MB). Las siguientes veces se usa desde caché local.

## Ejecutar el proyecto (recomendado)

No necesitas instalar nada manualmente: el script crea el entorno virtual, instala las dependencias, genera el dataset y arranca el servidor.

**Windows:** haz doble clic en `run.bat` (o ejecútalo desde una terminal).

**Mac / Linux:**
```bash
chmod +x run.sh
./run.sh
```

Cuando veas `Iniciando EcoMarket en http://127.0.0.1:5000`, abre esa dirección en tu navegador.

## Ejecución manual (alternativa)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python generar_dataset.py   # crea opiniones.csv de ejemplo
python app.py                # arranca en http://127.0.0.1:5000
```

## Estructura del proyecto

```
ecomarket/
├── app.py                # Rutas Flask (web + API JSON)
├── config.py              # Rutas de BD, modelo y dataset
├── modelos.py              # Clase Producto (validaciones)
├── repositorios.py         # Acceso a SQLite (patrón Repository)
├── servicios.py            # Lógica de negocio (GestorEcoMarket)
├── excepciones.py          # Excepciones propias del dominio
├── ml_analizador.py        # Extractor BETO + clasificador SVM de sentimientos
├── generar_dataset.py      # Genera opiniones.csv (dataset sintético reproducible)
├── templates/index.html    # Vista principal
├── static/                 # CSS, JS y assets
├── run.bat / run.sh        # Scripts de arranque automático
└── requirements.txt
```

## Notas

- `ecomarket.db`, `opiniones.csv` y `modelo_svm.joblib` se generan automáticamente al ejecutar el proyecto y no se suben al repositorio (ver `.gitignore`).
- Si compartes esta carpeta (o el repositorio) con otra persona, solo necesita tener Python instalado y ejecutar `run.bat` / `run.sh`; todo lo demás se instala solo.

### Problema conocido en Windows: "nombre de archivo demasiado largo"

Si el proyecto está en una ruta muy larga (por ejemplo, dentro de OneDrive con nombres de carpeta largos), la instalación de `torch` puede fallar por el límite de 260 caracteres de Windows. `run.bat` ya evita esto creando el entorno virtual en `%USERPROFILE%\.venvs\ecomarket` en vez de dentro del proyecto. Si aun así ocurre, puedes activar rutas largas de forma permanente (requiere permisos de administrador):

```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
