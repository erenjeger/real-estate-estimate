from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, url_for
from sqlalchemy import func, desc

from .extensions import db
from .models import Prediction, ModelMetric

main = Blueprint("main", __name__)


@main.get("/")
def dashboard():
    total_predictions = db.session.query(func.count(Prediction.id)).scalar() or 0
    average_price = db.session.query(
        func.avg(Prediction.predicted_price_idr)
    ).scalar()
    highest_price = db.session.query(
        func.max(Prediction.predicted_price_idr)
    ).scalar()
    latest_predictions = (
        Prediction.query.order_by(desc(Prediction.created_at)).limit(5).all()
    )
    latest_metric = ModelMetric.query.order_by(desc(ModelMetric.trained_at)).first()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        average_price=average_price or Decimal("0"),
        highest_price=highest_price or Decimal("0"),
        latest_predictions=latest_predictions,
        latest_metric=latest_metric,
    )


@main.route("/predict", methods=["GET"])
def predict():
    # The feature schema will be finalized after the dataset audit.
    return render_template("predict.html")


@main.get("/history")
def history():
    page = max(1, int(__import__("flask").request.args.get("page", 1)))
    pagination = Prediction.query.order_by(
        desc(Prediction.created_at)
    ).paginate(page=page, per_page=20, error_out=False)
    return render_template("history.html", pagination=pagination)
