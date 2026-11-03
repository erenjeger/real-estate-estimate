# Real Estate Estimate

A web application foundation for estimating Indonesian residential property prices using Multiple Linear Regression.

## Stack

- **Backend:** Python 3.12, Flask
- **Database:** PostgreSQL 16
- **ORM and migrations:** Flask-SQLAlchemy, Flask-Migrate
- **Frontend:** HTML, Bootstrap 5
- **Machine learning:** pandas, NumPy, scikit-learn, joblib
- **Application server:** Gunicorn

## Current status

This repository contains the initial Flask/PostgreSQL foundation:

- Dashboard summary
- Prediction page placeholder
- Prediction history page
- SQLAlchemy models for predictions, model metrics, and dataset sources
- PostgreSQL Docker Compose service
- Basic smoke tests

**Prediction is intentionally not enabled yet.** The dataset audit must determine the final feature schema, target definition, geographic coverage, and validation strategy before a trained model is integrated. No model accuracy or national market coverage is claimed at this stage.

## Local setup

### 1. Clone and configure

```bash
git clone https://github.com/erenjeger/real-estate-estimate.git
cd real-estate-estimate
cp .env.example .env
```

Edit `.env` and replace `SECRET_KEY` with a long random secret before using the app beyond local development.

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

PostgreSQL is exposed at `localhost:5432`. The default credentials in `.env.example` are for local development only.

### 3. Install Python dependencies

```bash
python -m venv .venv
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Create database tables

```bash
flask --app app init-db
```

For subsequent schema changes, use Flask-Migrate:

```bash
flask --app app db init
flask --app app db migrate -m "describe schema change"
flask --app app db upgrade
```

Commit generated migration scripts so other environments can reproduce schema changes.

### 5. Run the app

```bash
flask --app app run --debug
```

Open http://127.0.0.1:5000.

### Run tests

```bash
pytest
```

Tests use an in-memory SQLite database and do not require PostgreSQL. The application defaults to PostgreSQL.

## Docker

The `web` container connects to the database using the Compose service hostname `db`. For a fully containerized run, set this value in `.env`:

```text
DATABASE_URL=postgresql+psycopg://homeprice:homeprice_dev@db:5432/homeprice
```

Then initialize the schema and start the services:

```bash
docker compose run --rm web flask --app app init-db
docker compose up --build
```

The web service will be available at http://127.0.0.1:8000.

## Database tables

- `predictions`: submitted property characteristics and resulting estimates.
- `model_metrics`: evaluation metrics and metadata for model versions.
- `dataset_sources`: source provenance, license, collection time, and notes.

## Project phases

1. Dataset audit and selection.
2. Data cleaning and exploratory analysis.
3. Multiple Linear Regression experiments and evaluation.
4. Flask prediction workflow.
5. Dashboard and prediction history enhancements.
6. Testing and deployment hardening.

## Security notes

- Keep `.env` out of version control.
- Use a unique production `SECRET_KEY` and strong PostgreSQL credentials.
- Do not expose database ports publicly in production.
- Add authentication and authorization before exposing admin or dataset-management functions.
