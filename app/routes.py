from decimal import Decimal, InvalidOperation

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import desc, func, or_

from .extensions import db
from .models import ModelMetric, Prediction
from .regions import (
    CERTIFICATE_TYPES,
    DISTRICT_AREAS,
    PROPERTY_CONDITIONS,
    PROPERTY_TYPES,
    PROVINCE_CITIES,
)
from .services.prediction import predict_price

from . import format_idr

main = Blueprint("main", __name__)

WIB = timezone(timedelta(hours=7))
ACTIVITY_DAYS = 14

def local_date(value):
    return value.astimezone(WIB).date()

def compact_number(value):
    normalized = value.normalize()
    text = format(normalized, "f").rstrip("0").rstrip(".")
    return text or "0"

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
HISTORY_SORTS = {
    "newest": desc(Prediction.created_at),
    "oldest": Prediction.created_at.asc(),
    "price_desc": Prediction.predicted_price_idr.desc(),
    "price_asc": Prediction.predicted_price_idr.asc(),
}
HISTORY_PER_PAGE = 20


@main.get("/")
def dashboard():
    total_predictions = db.session.query(func.count(Prediction.id)).scalar() or 0
    average_price = db.session.query(func.avg(Prediction.predicted_price_idr)).scalar()
    highest_price = db.session.query(func.max(Prediction.predicted_price_idr)).scalar()
    latest_metric = ModelMetric.query.order_by(desc(ModelMetric.trained_at)).first()
    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        average_price=average_price or Decimal("0"),
        highest_price=highest_price or Decimal("0"),
        latest_metric=latest_metric,
        demo_metrics=load_demo_metrics(),
        activity=build_activity(),
    )


def build_activity():
    since = datetime.now(timezone.utc) - timedelta(days=ACTIVITY_DAYS - 1)
    rows = db.session.query(Prediction.created_at).filter(Prediction.created_at >= since).all()
    start = local_date(datetime.now(timezone.utc)) - timedelta(days=ACTIVITY_DAYS - 1)
    counts = {start + timedelta(days=offset): 0 for offset in range(ACTIVITY_DAYS)}
    for (created_at,) in rows:
        day = local_date(created_at)
        if day in counts:
            counts[day] += 1
    series = list(counts.values())
    total, last7, prev7 = sum(series), sum(series[-7:]), sum(series[:-7])
    max_count = max(series) or 1
    width, height, padding = 134, 36, 4
    step = (width - 2 * padding) / (ACTIVITY_DAYS - 1)
    points = [
        f"{padding + index * step:.1f},{height - padding - (count / max_count) * (height - 2 * padding):.1f}"
        for index, count in enumerate(series)
    ]
    return {
        "total": total,
        "last7": last7,
        "delta": last7 - prev7,
        "delta_visible": prev7 > 0,
        "spark": " ".join(points),
        "has_data": total > 0,
    }


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

    return render_template("predict.html", regions=PROVINCE_CITIES, districts=DISTRICT_AREAS, property_types=PROPERTY_TYPES, certificate_types=CERTIFICATE_TYPES, property_conditions=PROPERTY_CONDITIONS)


@main.get("/result/<int:prediction_id>")
def result(prediction_id):
    record = db.session.get(Prediction, prediction_id)
    if record is None:
        return "Data prediksi tidak ditemukan.", 404
    return render_template("result.html", prediction=record)


@main.get("/api/recent-predictions")
def recent_predictions():
    items = Prediction.query.order_by(desc(Prediction.created_at)).limit(5).all()
    return jsonify(
        items=[
            {
                "id": item.id,
                "city_regency": item.city_regency,
                "province": item.province,
                "land_area_m2": compact_number(item.land_area_m2),
                "price_label": format_idr(item.predicted_price_idr),
                "date": local_date(item.created_at).strftime("%d-%m-%Y"),
            }
            for item in items
        ]
    )


@main.get("/history")
def history():
    search = request.args.get("q", "").strip()
    province = request.args.get("province", "").strip()
    sort = request.args.get("sort", "newest")
    if sort not in HISTORY_SORTS:
        sort = "newest"
    page = max(1, request.args.get("page", 1, type=int) or 1)

    query = Prediction.query
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Prediction.city_regency.ilike(like),
                Prediction.province.ilike(like),
            )
        )
    if province:
        query = query.filter(Prediction.province == province)

    pagination = query.order_by(HISTORY_SORTS[sort]).paginate(
        page=page, per_page=HISTORY_PER_PAGE, error_out=False
    )
    provinces = [
        row[0]
        for row in db.session.query(Prediction.province).distinct().order_by(Prediction.province)
    ]
    filters = {
        key: value
        for key, value in (("q", search), ("province", province), ("sort", sort))
        if value and not (key == "sort" and value == "newest")
    }
    return render_template(
        "history.html",
        pagination=pagination,
        search=search,
        province=province,
        sort=sort,
        provinces=provinces,
        filters=filters,
    )
