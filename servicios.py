import sqlite3
from modelos import Producto
from repositorios import RepositorioProductosSQLite

try:
    from config import DB_PATH  # pyright: ignore[reportMissingImports]
except ImportError:
    DB_PATH = "ecomarket.db"


class GestorEcoMarket:
    def __init__(self, repo: RepositorioProductosSQLite = None):
        self.repo = repo or RepositorioProductosSQLite(ruta_bd=DB_PATH)

    def registrar_producto(self, nombre: str, precio: float, categoria: str, descripcion: str = "") -> Producto:
        nuevo_p = Producto(nombre=nombre, precio=precio, categoria=categoria, descripcion=descripcion)
        return self.repo.insertar(nuevo_p)

    def obtener_catalogo(self):
        return self.repo.listar()

    def buscar_producto(self, id_p: int):
        return self.repo.buscar_por_id(id_p)

    def actualizar_producto(self, id_p: int, nombre: str = None, precio: float = None, categoria: str = None, descripcion: str = None):
        producto = self.buscar_producto(id_p)
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        if categoria is not None:
            producto.categoria = categoria
        if descripcion is not None:
            producto.descripcion = descripcion
        self.repo.actualizar(producto)
        return producto

    def eliminar_producto(self, id_p: int):
        self.repo.eliminar(id_p)

    # --- Opiniones (almacenadas en la misma DB local) -----------------
    def guardar_opinion(self, texto: str, sentimiento: str):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS opiniones (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT NOT NULL, sentimiento TEXT NOT NULL)"
            )
            cursor.execute("INSERT INTO opiniones (texto, sentimiento) VALUES (?, ?)", (texto, sentimiento))
            conn.commit()

    def resumen_opiniones(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sentimiento, COUNT(*) FROM opiniones GROUP BY sentimiento")
            return cursor.fetchall()

    def contar_opiniones(self) -> int:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM opiniones")
            return cursor.fetchone()[0]

    def sembrar_catalogo_inicial(self) -> int:
        # Inserta algunos productos de ejemplo si la tabla está vacía.
        existentes = self.obtener_catalogo()
        if existentes:
            return len(existentes)
        ejemplo = [
            ("Cepillo de bambú", 5.99, "hogar", "Cepillo ecológico de cerdas suaves"),
            ("Bolsa de tela", 12.5, "accesorios", "Bolsa reutilizable resistente"),
            ("Jabón artesanal", 3.75, "cuidado", "Jabón natural sin fragancias fuertes"),
        ]
        for nombre, precio, categoria, descripcion in ejemplo:
            try:
                self.registrar_producto(nombre, precio, categoria, descripcion)
            except Exception:
                pass
        return len(self.obtener_catalogo())
