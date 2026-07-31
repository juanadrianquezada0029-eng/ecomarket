from abc import ABC, abstractmethod
import sqlite3
from modelos import Producto
from excepciones import ProductoNoEncontradoError

class Repositorio(ABC):
    @abstractmethod
    def insertar(self, objeto):
        pass

    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def buscar_por_id(self, id_obj):
        pass

    @abstractmethod
    def actualizar(self, objeto):
        pass

    @abstractmethod
    def eliminar(self, id_obj):
        pass

class RepositorioProductosSQLite(Repositorio):
    def __init__(self, ruta_bd="ecomarket.db"):
        self.ruta_bd = ruta_bd
        self._crear_tabla()

    def _crear_tabla(self):
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    descripcion TEXT
                )
            """)
            conn.commit()

    def insertar(self, producto: Producto) -> Producto:
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre, precio, categoria, descripcion) VALUES (?, ?, ?, ?)",
                (producto.nombre, producto.precio, producto.categoria, producto.descripcion)
            )
            producto._id = cursor.lastrowid
            conn.commit()
            return producto

    def listar(self) -> list[Producto]:
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, precio, categoria, descripcion FROM productos")
            filas = cursor.fetchall()
            return [Producto(id_producto=f[0], nombre=f[1], precio=f[2], categoria=f[3], descripcion=f[4]) for f in filas]

    def buscar_por_id(self, id_obj: int) -> Producto:
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, precio, categoria, descripcion FROM productos WHERE id = ?", (id_obj,))
            fila = cursor.fetchone()
            if not fila:
                raise ProductoNoEncontradoError(f"Producto con ID {id_obj} no encontrado.")
            return Producto(id_producto=fila[0], nombre=fila[1], precio=fila[2], categoria=fila[3], descripcion=fila[4])

    def actualizar(self, producto: Producto):
        if not producto.id:
            raise ProductoNoEncontradoError("El producto a actualizar debe tener un ID válido.")
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET nombre = ?, precio = ?, categoria = ?, descripcion = ? WHERE id = ?",
                (producto.nombre, producto.precio, producto.categoria, producto.descripcion, producto.id)
            )
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(f"No se pudo actualizar el producto con ID {producto.id}.")
            conn.commit()

    def eliminar(self, id_obj: int):
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_obj,))
            if cursor.rowcount == 0:
                raise ProductoNoEncontradoError(f"No se encontró el producto ID {id_obj} para eliminar.")
            conn.commit()
