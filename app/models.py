from datetime import datetime, timezone

from sqlalchemy import BigInteger, Integer

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


ID_TYPE = BigInteger().with_variant(Integer, "sqlite")


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(ID_TYPE, primary_key=True)
    province = db.Column(db.String(100), nullable=False, index=True)
    city_regency = db.Column(db.String(120), nullable=False, index=True)
    district_area = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(100), nullable=False)
    land_area_m2 = db.Column(db.Numeric(12, 2), nullable=False)
    building_area_m2 = db.Column(db.Numeric(12, 2), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    floors = db.Column(db.Integer, nullable=False)
    building_age_years = db.Column(db.Integer, nullable=False)
    certificate_type = db.Column(db.String(50), nullable=False)
    property_condition = db.Column(db.String(80), nullable=False)
    predicted_price_idr = db.Column(db.Numeric(20, 2), nullable=False)
    model_version = db.Column(db.String(50), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )


class ModelMetric(db.Model):
    __tablename__ = "model_metrics"

    id = db.Column(ID_TYPE, primary_key=True)
    model_version = db.Column(db.String(50), nullable=False, unique=True)
    mae_idr = db.Column(db.Numeric(20, 4), nullable=True)
    rmse_idr = db.Column(db.Numeric(20, 4), nullable=True)
    r2 = db.Column(db.Numeric(12, 8), nullable=True)
    dataset_rows = db.Column(db.Integer, nullable=False)
    evaluation_strategy = db.Column(db.String(120), nullable=True)
    trained_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )


class DatasetSource(db.Model):
    __tablename__ = "dataset_sources"

    id = db.Column(ID_TYPE, primary_key=True)
    source_name = db.Column(db.String(200), nullable=False)
    source_url = db.Column(db.Text, nullable=True)
    license_name = db.Column(db.String(120), nullable=True)
    collected_at = db.Column(db.DateTime(timezone=True), nullable=True)
    row_count = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow
    )
