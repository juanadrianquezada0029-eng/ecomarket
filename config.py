import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "ecomarket.db")
MODEL_PATH = os.path.join(BASE_DIR, "modelo_svm.joblib")
CSV_PATH = os.path.join(BASE_DIR, "opiniones.csv")
SEMILLA = 12345
