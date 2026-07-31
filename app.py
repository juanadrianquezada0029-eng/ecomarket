import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from servicios import GestorEcoMarket
from ml_analizador import AnalizadorOpiniones

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "ecomarket.db")
MODEL_PATH = os.path.join(BASE_DIR, "modelo_svm.joblib")
CSV_PATH = os.path.join(BASE_DIR, "opiniones.csv")

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def preparar_tabla_opiniones():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opiniones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                sentimiento TEXT NOT NULL
            )
        """)
        conn.commit()


def guardar_opinion(texto: str, sentimiento: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO opiniones (texto, sentimiento) VALUES (?, ?)", (texto, sentimiento))
        conn.commit()


def obtener_resumen_opiniones():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sentimiento, COUNT(*) FROM opiniones GROUP BY sentimiento")
        return cursor.fetchall()


def inicializar_modelo():
    analizador = AnalizadorOpiniones()
    if os.path.exists(MODEL_PATH):
        analizador.clasificador.cargar(MODEL_PATH)
    else:
        analizador.entrenar_con_csv(CSV_PATH, MODEL_PATH)
    return analizador


@app.route("/")
def index():
    preparar_tabla_opiniones()
    gestor = GestorEcoMarket()
    productos = gestor.obtener_catalogo()
    resumen = obtener_resumen_opiniones()
    return render_template("index.html", productos=productos, resumen=resumen)


@app.route("/api/productos", methods=["POST", "OPTIONS"])
def api_crear_producto():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    data = request.json
    try:
        nombre = data.get("nombre")
        precio = float(data.get("precio", 0))
        categoria = data.get("categoria")
        descripcion = data.get("descripcion", "")

        gestor = GestorEcoMarket()
        producto = gestor.registrar_producto(nombre, precio, categoria, descripcion)

        return jsonify({
            "success": True,
            "producto": {
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "categoria": producto.categoria,
                "descripcion": producto.descripcion,
            }
        }), 201
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/api/analizar", methods=["POST", "OPTIONS"])
def api_analizar_opinion():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    data = request.json
    texto = data.get("texto", "")

    try:
        analizador = inicializar_modelo()
        sentimiento = analizador.predecir_sentimiento(texto)
        guardar_opinion(texto, sentimiento)
        resumen = obtener_resumen_opiniones()
        return jsonify({"success": True, "sentimiento": sentimiento, "resumen": resumen})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") != "0"
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=debug_mode)
