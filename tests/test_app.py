from pathlib import Path

import pytest

from app import create_app
from app.extensions import db
from training.train_model import train


@pytest.fixture()
def client(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-secret",
        "MODEL_PATH": str(tmp_path / "home_price_model.joblib"),
    })
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_dashboard_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_predict_page_renders_demo_disclaimer(client):
    response = client.get("/predict")
    assert response.status_code == 200
    assert "data sintetis".encode("utf-8") in response.data
    assert "tidak boleh digunakan untuk keputusan transaksi".encode("utf-8") in response.data


def test_prediction_requires_trained_model(client):
    response = client.post("/predict", data={
        "province": "DKI Jakarta",
        "city_regency": "Jakarta Selatan",
        "district_area": "Kawasan Perumahan",
        "property_type": "Rumah Tapak",
        "certificate_type": "SHM",
        "property_condition": "Baik",
        "land_area_m2": "120",
        "building_area_m2": "90",
        "bedrooms": "3",
        "bathrooms": "2",
        "floors": "1",
        "building_age_years": "5",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Model belum dilatih" in response.data


def test_history_renders_empty_state(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert b"Belum ada prediksi tersimpan" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_synthetic_training_produces_model_and_metrics(tmp_path):
    root = Path(__file__).resolve().parents[1]
    data_path = root / "data/raw/home_price_demo_synthetic.csv"
    model_path = tmp_path / "home_price_model.joblib"
    metrics_path = tmp_path / "model_metrics.json"

    metrics = train(data_path, model_path, metrics_path)

    assert model_path.exists()
    assert metrics_path.exists()
    assert metrics["data_origin"] == "SYNTHETIC_DEMO_ONLY"
    assert metrics["rows_total"] == 1500
