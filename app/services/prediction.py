from pathlib import Path

import joblib
import pandas as pd
from flask import current_app


def load_model_bundle():
    model_path = Path(current_app.config["MODEL_PATH"])
    if not model_path.exists():
        return None
    return joblib.load(model_path)


def predict_price(payload):
    bundle = load_model_bundle()
    if bundle is None:
        raise FileNotFoundError("Model belum dilatih. Jalankan: python -m training.train_model")

    frame = pd.DataFrame([{key: payload[key] for key in bundle["features"]}])
    value = float(bundle["pipeline"].predict(frame)[0])
    if value <= 0:
        raise ValueError("Model menghasilkan estimasi tidak positif.")
    return value, bundle["model_version"]
