import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SECRET_KEY": "test-secret",
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


def test_predict_page_explains_model_status(client):
    response = client.get("/predict")
    assert response.status_code == 200
    assert b"Model belum tersedia" in response.data


def test_history_renders_empty_state(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert b"Belum ada prediksi tersimpan" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
