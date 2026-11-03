import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://homeprice:homeprice_dev@localhost:5432/homeprice",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/home_price_model.joblib")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
