from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy import desc, func

from .extensions import db
from .models import ModelMetric, Prediction
from .services.prediction import predict_price

main = Blueprint("main", __name__)

NUMERIC_FIELDS = {
    "land_area_m2": float,
    "building_area_m2": float,
    "bedrooms": int,
    "bathrooms": int,
    "floors": int,
    "building_age_years": int,
}
CATEGORY_FIELDS = [
    "province", "city_regency", "district_area", "property_type",
    "certificate_type", "property_condition",
]


@main.get("/")
def dashboard():
    total_predictions = db.session.query(func.count(Prediction.id)).scalar() or 0
    average_price = db.session.query(func.avg(Prediction.predicted_price_idr)).scalar()
    highest_price = db.session.query(func.max(Prediction.predicted_price_idr)).scalar()
    latest_predictions = Prediction.query.order_by(desc(Prediction.created_at)).limit(5).all()
    latest_metric = ModelMetric.query.order_by(desc(ModelMetric.trained_at)).first()
    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        average_price=average_price or Decimal("0"),
        highest_price=highest_price or Decimal("0"),
        latest_predictions=latest_predictions,
        latest_metric=latest_metric,
        demo_metrics=load_demo_metrics(),
    )


def load_demo_metrics():
    import json
    from pathlib import Path
    path = Path(current_app.config["MODEL_PATH"]).with_name("model_metrics.json")
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@main.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            payload = {}
            for field in CATEGORY_FIELDS:
                payload[field] = request.form.get(field, "").strip()
                if not payload[field]:
                    raise ValueError(f"Kolom {field} wajib diisi.")
            for field, converter in NUMERIC_FIELDS.items():
                payload[field] = converter(request.form.get(field, ""))
            if payload["land_area_m2"] <= 0 or payload["building_area_m2"] <= 0:
                raise ValueError("Luas tanah dan luas bangunan harus lebih dari nol.")
            if payload["building_area_m2"] > payload["land_area_m2"] * 2:
                raise ValueError("Luas bangunan terlalu besar dibandingkan luas tanah.")
            if min(payload["bedrooms"], payload["bathrooms"], payload["floors"]) < 1:
                raise ValueError("Kamar tidur, kamar mandi, dan lantai minimal 1.")
            if payload["building_age_years"] < 0:
                raise ValueError("Usia bangunan tidak boleh negatif.")

            predicted_price, model_version = predict_price(payload)
            record = Prediction(
                **payload,
                predicted_price_idr=Decimal(str(round(predicted_price, 2))),
                model_version=model_version,
            )
            db.session.add(record)
            db.session.commit()
            return redirect(url_for("main.result", prediction_id=record.id))
        except FileNotFoundError as exc:
            flash(str(exc), "warning")
        except (ValueError, TypeError, InvalidOperation) as exc:
            flash(str(exc) or "Input tidak valid.", "danger")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Prediction request failed")
            flash("Prediksi gagal diproses. Periksa konfigurasi model dan database.", "danger")

    return render_template("predict.html")


@main.get("/result/<int:prediction_id>")
def result(prediction_id):
    record = db.session.get(Prediction, prediction_id)
    if record is None:
        return "Data prediksi tidak ditemukan.", 404
    return render_template("result.html", prediction=record)


@main.get("/history")
def history():
    page = max(1, request.args.get("page", 1, type=int) or 1)
    pagination = Prediction.query.order_by(desc(Prediction.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("history.html", pagination=pagination)
