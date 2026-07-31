import os
import pandas as pd
import numpy as np
from excepciones import ModeloNoEntrenadoError

# Dependencias pesadas o opcionales: silenciar reportMissingImports para evitar
# ruido en editores cuando no están instaladas. En tiempo de ejecución se
# comprobará su presencia y se lanzará un error claro si faltan.
try:
    import joblib  # pyright: ignore[reportMissingImports]
except Exception:
    joblib = None

try:
    import torch  # pyright: ignore[reportMissingImports]
except Exception:
    torch = None

try:
    from transformers import AutoTokenizer, AutoModel  # pyright: ignore[reportMissingImports]
except Exception:
    AutoTokenizer = None
    AutoModel = None

try:
    from sklearn.svm import LinearSVC  # pyright: ignore[reportMissingImports]
    from sklearn.model_selection import train_test_split  # pyright: ignore[reportMissingImports]
    from sklearn.metrics import classification_report, confusion_matrix  # pyright: ignore[reportMissingImports]
except Exception:
    LinearSVC = None
    train_test_split = None
    classification_report = None
    confusion_matrix = None

class ExtractorBETO:
    def __init__(self, modelo_nombre="dccuchile/bert-base-spanish-wwm-cased"):
        if AutoTokenizer is None or AutoModel is None or torch is None:
            raise ImportError(
                "ExtractorBETO requiere los paquetes 'transformers' y 'torch'. "
                "Instálalos con: pip install transformers torch"
            )
        self.tokenizer = AutoTokenizer.from_pretrained(modelo_nombre)
        self.modelo = AutoModel.from_pretrained(modelo_nombre)
        self.modelo.eval()

    def transformar(self, textos: list[str]) -> np.ndarray:
        textos = [t if t.strip() else "vacío" for t in textos]
        if self.tokenizer is None or self.modelo is None or torch is None:
            raise RuntimeError("ExtractorBETO no está disponible: faltan dependencias o no se inicializó correctamente.")
        tokens = self.tokenizer(textos, padding=True, truncation=True, max_length=128, return_tensors="pt")
        with torch.no_grad():
            outputs = self.modelo(**tokens)
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        return embeddings

class ClasificadorSentimientosSVM:
    def __init__(self):
        if LinearSVC is None:
            raise ImportError("ClasificadorSentimientosSVM requiere 'scikit-learn'. Instálalo con: pip install scikit-learn")
        self.modelo = LinearSVC(class_weight="balanced", random_state=42, max_iter=2000)

    def entrenar(self, X, y):
        self.modelo.fit(X, y)

    def predecir(self, X):
        return self.modelo.predict(X)

    def guardar(self, ruta="modelo_svm.joblib"):
        if joblib is None:
            raise ImportError("Para guardar/recuperar el modelo se necesita 'joblib'. Instálalo con: pip install joblib")
        joblib.dump(self.modelo, ruta)

    def cargar(self, ruta="modelo_svm.joblib"):
        if joblib is None:
            raise ImportError("Para cargar el modelo se necesita 'joblib'. Instálalo con: pip install joblib")
        self.modelo = joblib.load(ruta)

class AnalizadorOpiniones:
    DATASET_POR_DEFECTO = [
        ("Excelente producto ecológico, muy recomendado", "positivo"),
        ("Mala calidad, se rompió al primer uso", "negativo"),
        ("El empaque es correcto y llegó a tiempo", "neutral"),
        ("Me encantó el cepillo de bambú, suave y natural", "positivo"),
        ("Pésimo servicio de entrega, llegó tarde", "negativo"),
        ("Cumple con su función, nada extraordinario", "neutral"),
    ] * 20

    def __init__(self):
        # Inicialización perezosa/segura: las dependencias requeridas lanzarán
        # ImportError con instrucciones claras si faltan (p. ej. torch, transformers).
        self.extractor = None
        self.clasificador = None
        try:
            self.extractor = ExtractorBETO()
            self.clasificador = ClasificadorSentimientosSVM()
        except ImportError:
            # Dejar en None para permitir rutas alternativas (TF-IDF) o entrenamiento
            # con recursos limitados; las funciones que necesiten los modelos deben
            # comprobar su presencia y arrojar errores adecuados.
            self.extractor = None
            self.clasificador = None

    def entrenar_con_csv(self, ruta_csv="opiniones.csv", ruta_modelo="modelo_svm.joblib"):
        if self.extractor is None or self.clasificador is None:
            raise ModeloNoEntrenadoError("No están disponibles las dependencias necesarias para entrenar o inferir el modelo.")

        if os.path.exists(ruta_csv):
            df = pd.read_csv(ruta_csv)
        else:
            df = pd.DataFrame(self.DATASET_POR_DEFECTO, columns=["texto", "etiqueta"])

        X_embeddings = self.extractor.transformar(df["texto"].tolist())
        y = df["etiqueta"]

        X_train, X_test, y_train, y_test = train_test_split(
            X_embeddings, y, test_size=0.2, random_state=42, stratify=y
        )

        self.clasificador.entrenar(X_train, y_train)
        preds = self.clasificador.predecir(X_test)

        print("--- REPORTE DE EVALUACIÓN ---")
        print(classification_report(y_test, preds))
        print("--- MATRIZ DE CONFUSIÓN ---")
        print(confusion_matrix(y_test, preds))

        self.clasificador.guardar(ruta_modelo)

    def predecir_sentimiento(self, texto: str) -> str:
        if self.extractor is None or self.clasificador is None:
            raise ModeloNoEntrenadoError("El analizador no está inicializado o faltan dependencias.")
        vector = self.extractor.transformar([texto])
        pred = self.clasificador.predecir(vector)
        return pred[0]
