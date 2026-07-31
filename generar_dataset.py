"""Generación del dataset `opiniones.csv`.

FUENTE DE LOS DATOS
-------------------
Corpus sintético de elaboración propia para uso académico. No se extrajo de
ninguna plataforma comercial, por lo que no hay restricciones de licencia ni
datos personales involucrados (licencia equivalente a CC0 / dominio público).

MÉTODO
------
Cada opinión se construye combinando fragmentos escritos a mano (apertura +
núcleo valorativo + cierre) propios de cada clase. La combinación usa una
semilla fija, así que el CSV es reproducible: ejecutarlo dos veces produce
exactamente el mismo archivo.

Se generan opiniones ÚNICAS (sin duplicados) y balanceadas entre las tres
clases: positivo, negativo y neutral.
"""

import random

import pandas as pd

try:
    from config import CSV_PATH, SEMILLA  # pyright: ignore[reportMissingImports]
except ImportError:
    # Valores por defecto si no existe config.py (útil para ejecuciones aisladas)
    CSV_PATH = "opiniones.csv"
    SEMILLA = 12345

OPINIONES_POR_CLASE = 110

# --------------------------------------------------------------- POSITIVO
POS_APERTURA = [
    "Excelente compra",
    "Quedé encantada con el producto",
    "Superó mis expectativas",
    "Me encantó todo",
    "Muy buena experiencia",
    "Estoy feliz con mi pedido",
    "Compra totalmente acertada",
    "Producto de primera calidad",
    "La verdad me sorprendió gratamente",
    "Repetiría la compra sin dudarlo",
    "Justo lo que buscaba",
    "Vale cada centavo",
]
POS_NUCLEO = [
    "el cepillo de bambú es suave y no se deshilacha",
    "la bolsa de tela aguanta mucho peso",
    "el jabón artesanal huele delicioso y dura semanas",
    "los materiales se sienten resistentes y naturales",
    "el empaque es de cartón reciclado y sin plástico",
    "el envío llegó dos días antes de lo previsto",
    "la atención al cliente respondió en minutos",
    "la calidad del algodón orgánico se nota al tacto",
    "el producto viene tal cual las fotos de la tienda",
    "el precio es justísimo para lo que ofrece",
]
POS_CIERRE = [
    "lo recomiendo al cien por ciento",
    "ya encargué otro para regalar",
    "una tienda ecológica confiable",
    "seguiré comprando aquí",
    "felicito al equipo por el detalle",
    "cumplieron todo lo que prometían",
    "es un cambio real hacia lo sostenible",
    "gracias por el servicio tan atento",
]

# --------------------------------------------------------------- NEGATIVO
NEG_APERTURA = [
    "Muy mala experiencia",
    "Estoy decepcionado",
    "No lo recomiendo para nada",
    "Pésima compra",
    "Me arrepiento de haber pedido",
    "Un desastre completo",
    "Perdí mi dinero",
    "Terrible servicio",
    "Nada que ver con lo anunciado",
    "Bastante frustrante todo",
    "No vuelvo a comprar aquí",
    "Una lástima de producto",
]
NEG_NUCLEO = [
    "el producto llegó roto dentro de la caja",
    "el cepillo se deshizo al segundo uso",
    "la bolsa se descosió cargando apenas dos kilos",
    "el jabón venía derretido y pegado al empaque",
    "el envío tardó tres semanas sin explicación",
    "nadie contestó mis correos ni mis mensajes",
    "me enviaron un artículo diferente al que pedí",
    "el material se siente plástico y barato",
    "cobraron el envío dos veces a mi tarjeta",
    "el olor era desagradable desde que lo abrí",
]
NEG_CIERRE = [
    "y todavía espero mi reembolso",
    "nunca más compro en esta tienda",
    "deberían revisar su control de calidad",
    "no vale ni la mitad del precio",
    "una pérdida total de tiempo",
    "el soporte fue completamente inútil",
    "me obligaron a pagar la devolución",
    "no cumple nada de lo que promete",
]

# ---------------------------------------------------------------- NEUTRAL
NEU_APERTURA = [
    "El producto cumple",
    "Es aceptable",
    "Ni bueno ni malo",
    "Nada extraordinario",
    "Es lo que se esperaba",
    "Sin sorpresas",
    "Del promedio",
    "Cumple su función básica",
    "Se puede usar",
    "Un producto correcto",
    "Está bien sin más",
    "Normal para el precio",
]
NEU_NUCLEO = [
    "el empaque llegó en condiciones normales",
    "el envío tomó los días indicados en la página",
    "el tamaño coincide con la descripción",
    "el material es el estándar del mercado",
    "el precio está dentro de lo habitual",
    "la entrega se hizo en la fecha estimada",
    "el color es parecido al de la foto",
    "la presentación es simple y funcional",
    "el peso corresponde a lo publicado",
    "la textura es la común en este tipo de artículo",
]
NEU_CIERRE = [
    "no tengo mucho más que comentar",
    "habría que probarlo más tiempo",
    "supongo que sirve para el uso diario",
    "ni lo recomiendo ni lo descarto",
    "quizá vuelva a comprarlo, quizá no",
    "cumple lo mínimo esperado",
    "es una opción entre muchas",
    "sin comentarios adicionales",
]

PLANTILLAS = {
    "positivo": (POS_APERTURA, POS_NUCLEO, POS_CIERRE),
    "negativo": (NEG_APERTURA, NEG_NUCLEO, NEG_CIERRE),
    "neutral": (NEU_APERTURA, NEU_NUCLEO, NEU_CIERRE),
}

CONECTORES = [", ", ": ", " y ", ". Además, ", " pero al final ", ", así que "]

# Aperturas concesivas: permiten mezclar vocabulario de OTRA clase dentro de
# una opinión, tal como escribe un cliente real ("aunque tardó, me encantó").
# Esto crea solapamiento léxico entre clases y evita que el clasificador
# alcance un 100% artificial que no representa ningún reto de aprendizaje.
CONCESIVAS = [
    "Aunque",
    "Si bien",
    "A pesar de que",
    "Es cierto que",
]

# Proporción de opiniones con estructura concesiva (mezcla de vocabulario).
PROPORCION_MIXTAS = 0.35

# --- OPINIONES DE FRONTERA -------------------------------------------------
# Fragmentos que las TRES clases comparten. Producen opiniones genuinamente
# ambiguas, del tipo que en un corpus real dos anotadores humanos etiquetarían
# distinto. Sin ellas el dataset sería linealmente separable al 100% y las
# métricas no medirían ninguna capacidad real de generalización.
FRONTERA_APERTURA = [
    "Recibí el pedido",
    "Ya probé el producto",
    "Llegó el paquete",
    "Compré este artículo la semana pasada",
    "Después de un par de usos",
    "Tras probarlo unos días",
]
FRONTERA_NUCLEO = [
    "el envío llegó dentro del plazo",
    "el empaque venía sellado",
    "el artículo coincide con la descripción",
    "el precio es el que aparecía publicado",
    "la entrega la hizo el mensajero habitual",
    "el producto funciona como cualquier otro",
]
FRONTERA_CIERRE = [
    "veremos qué tal resulta con el tiempo",
    "todavía es pronto para opinar",
    "no sabría qué decir todavía",
    "cada quien tendrá su propia impresión",
    "lo dejo a criterio de cada comprador",
]

PROPORCION_FRONTERA = 0.12


def _nucleo_ajeno(etiqueta: str, rng: random.Random) -> str:
    """Devuelve un núcleo tomado de una clase distinta a `etiqueta`."""
    otras = [e for e in PLANTILLAS if e != etiqueta]
    _, nucleos, _ = PLANTILLAS[rng.choice(otras)]
    return rng.choice(nucleos)


def _generar_clase(etiqueta: str, cantidad: int, rng: random.Random) -> list[tuple[str, str]]:
    aperturas, nucleos, cierres = PLANTILLAS[etiqueta]
    vistos: set[str] = set()
    resultado: list[tuple[str, str]] = []
    intentos = 0
    limite = cantidad * 400

    while len(resultado) < cantidad and intentos < limite:
        intentos += 1
        apertura = rng.choice(aperturas)
        nucleo = rng.choice(nucleos)
        cierre = rng.choice(cierres)

        sorteo = rng.random()

        if sorteo < PROPORCION_FRONTERA:
            # Caso de frontera: vocabulario 100% compartido entre clases.
            texto = (
                f"{rng.choice(FRONTERA_APERTURA)}, {rng.choice(FRONTERA_NUCLEO)}. "
                f"{rng.choice(FRONTERA_CIERRE).capitalize()}."
            )
        elif sorteo < PROPORCION_MIXTAS:
            # Opinión mixta: la concesión trae léxico de otra clase, pero la
            # valoración final (y por tanto la etiqueta) es la de esta clase.
            concesiva = rng.choice(CONCESIVAS)
            ajeno = _nucleo_ajeno(etiqueta, rng)
            texto = f"{concesiva} {ajeno}, {apertura.lower()}: {nucleo}. {cierre.capitalize()}."
        else:
            conector = rng.choice(CONECTORES)
            texto = f"{apertura}{conector}{nucleo}. {cierre.capitalize()}."

        # Normalizamos espacios y evitamos dobles signos.
        texto = " ".join(texto.split()).replace("..", ".").replace(" ,", ",")
        if texto in vistos:
            continue
        vistos.add(texto)
        resultado.append((texto, etiqueta))

    if len(resultado) < cantidad:
        raise RuntimeError(
            f"Solo se generaron {len(resultado)} opiniones únicas para '{etiqueta}'. "
            "Agrega más fragmentos a las listas."
        )
    return resultado


def generar_dataset(ruta_csv: str = CSV_PATH, por_clase: int = OPINIONES_POR_CLASE) -> pd.DataFrame:
    """Construye y guarda el CSV con columnas `texto` y `etiqueta`."""
    rng = random.Random(SEMILLA)
    filas: list[tuple[str, str]] = []
    for etiqueta in PLANTILLAS:
        filas.extend(_generar_clase(etiqueta, por_clase, rng))

    rng.shuffle(filas)
    df = pd.DataFrame(filas, columns=["texto", "etiqueta"])
    df = df.drop_duplicates(subset="texto").reset_index(drop=True)
    df.to_csv(ruta_csv, index=False, encoding="utf-8")

    print(f"[OK] Dataset generado en: {ruta_csv}")
    print(f"     Total de opiniones únicas: {len(df)}")
    print("     Distribución por clase:")
    for etiqueta, cantidad in df["etiqueta"].value_counts().items():
        print(f"       - {etiqueta}: {cantidad}")
    return df


if __name__ == "__main__":
    generar_dataset()
