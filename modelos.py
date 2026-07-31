from excepciones import ProductoInvalidoError

class Producto:
    def __init__(self, nombre: str, precio: float, categoria: str, descripcion: str = "", id_producto: int | None = None):
        self._id = id_producto
        self.nombre = nombre
        self.precio = precio
        self.categoria = categoria
        self.descripcion = descripcion
        self.validar()

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ProductoInvalidoError("El nombre del producto no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor: float):
        if valor <= 0:
            raise ProductoInvalidoError("El precio debe ser un valor mayor a cero.")
        self._precio = float(valor)

    @property
    def categoria(self):
        return self._categoria

    @categoria.setter
    def categoria(self, valor: str):
        if not valor or not valor.strip():
            raise ProductoInvalidoError("La categoría es requerida.")
        self._categoria = valor.strip()

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str):
        self._descripcion = valor.strip() if valor else ""

    def validar(self):
        """Valida las reglas del negocio."""
        if self._precio <= 0 or not self._nombre or not self._categoria:
            raise ProductoInvalidoError("Datos inválidos detectados en la verificación.")

    def __str__(self):
        return f"ID {self._id if self._id else 'N/A'} - {self._nombre} - ${self._precio:.2f} ({self._categoria})"
