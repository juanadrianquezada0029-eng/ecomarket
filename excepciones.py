class EcoMarketError(Exception):
    """Excepción base para la aplicación EcoMarket."""
    pass

class ProductoInvalidoError(EcoMarketError):
    """Lanzada cuando los datos de un producto no son válidos."""
    pass

class ProductoNoEncontradoError(EcoMarketError):
    """Lanzada cuando un producto no existe en el repositorio."""
    pass


class ModeloNoEntrenadoError(EcoMarketError):
    """Lanzada cuando se intenta usar el analizador pero el modelo no está listo."""
    pass
