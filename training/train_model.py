"""Train a demo Multiple Linear Regression model.

This script intentionally marks the artifact as synthetic-demo-only. Metrics
from this dataset are pipeline smoke-test metrics, not real-market evidence.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data/raw/home_price_demo_synthetic.csv"
DEFAULT_MODEL = ROOT / "artifacts/home_price_model.joblib"
DEFAULT_METRICS = ROOT / "artifacts/model_metrics.json"

TARGET = "price_idr"
NUMERIC = [
    "land_area_m2", "building_area_m2", "bedrooms", "bathrooms",
    "floors", "building_age_years",
]
CATEGORICAL = [
    "province", "city_regency", "district_area", "property_type",
    "certificate_type", "property_condition",
]
FEATURES = CATEGORICAL + NUMERIC
REQUIRED = FEATURES + [TARGET, "data_origin"]


def train(data_path=DEFAULT_DATA, model_path=DEFAULT_MODEL, metrics_path=DEFAULT_METRICS):
    df = pd.read_csv(data_path)
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    origins = set(df["data_origin"].dropna().astype(str).unique())
    is_synthetic = origins == {"SYNTHETIC_DEMO_ONLY"}
    if not is_synthetic:
        raise ValueError(
            "This demo trainer expects data_origin=SYNTHETIC_DEMO_ONLY. "
            "Build a separately reviewed training configuration for real data."
        )

    df = df[REQUIRED].copy()
    for col in NUMERIC + [TARGET]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[TARGET])
    df = df[df[TARGET] > 0]
    if len(df) < 30:
        raise ValueError("At least 30 valid rows are required for this demo training run.")

    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    preprocessor = ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC),
        ("categorical", categorical_pipe, CATEGORICAL),
    ])
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression()),
    ])
    pipeline.fit(X_train, y_train)

    predicted = pipeline.predict(X_test)
    metrics = {
        "model_version": "demo-synthetic-v1",
        "data_origin": "SYNTHETIC_DEMO_ONLY",
        "is_real_market_model": False,
        "rows_total": int(len(df)),
        "rows_train": int(len(X_train)),
        "rows_test": int(len(X_test)),
        "mae_idr": float(mean_absolute_error(y_test, predicted)),
        "rmse_idr": float(mean_squared_error(y_test, predicted) ** 0.5),
        "r2": float(r2_score(y_test, predicted)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "features": FEATURES,
        "target": TARGET,
        "split": "random 80/20, random_state=42",
        "warning": "Synthetic demo metrics only; not evidence of real Indonesian market performance.",
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "pipeline": pipeline,
        "features": FEATURES,
        "model_version": metrics["model_version"],
        "data_origin": metrics["data_origin"],
    }, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    args = parser.parse_args()
    train(args.data, args.model, args.metrics)
