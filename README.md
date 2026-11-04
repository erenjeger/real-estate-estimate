# Real Estate Estimate

Flask + PostgreSQL application for a HomePrice Prediction System. It includes a clearly labelled synthetic demo ML pipeline.

## Stack
- Python 3.12, Flask
- PostgreSQL 16, SQLAlchemy, Flask-Migrate
- Bootstrap 5
- pandas, NumPy, scikit-learn, joblib

## Synthetic demo mode

The repository includes `data/raw/home_price_demo_synthetic.csv` with 1,500 generated records. It is **synthetic demonstration data**, not actual listing, appraisal, or transaction data. Metrics from this dataset must not be reported as real-world accuracy or used for property decisions.

### Train the demo model

After installing requirements:

```bash
python -m training.train_model
```

This creates:
- `artifacts/home_price_model.joblib`
- `artifacts/model_metrics.json`

The training script refuses datasets not marked `SYNTHETIC_DEMO_ONLY` so this demo workflow cannot silently be used as the real research pipeline.

### Enable demo prediction

1. Ensure PostgreSQL is running and `.env` is configured.
2. Create/update the database schema. For a fresh local database:

   ```bash
   flask --app app init-db
   ```

   If you have an existing database created from an earlier version of this project, back it up and recreate the local development database, or create and apply a Flask-Migrate migration for the changed `predictions` table. `create_all` does not alter existing tables.

3. Start Flask:

   ```bash
   flask --app app run --debug
   ```

4. Open http://127.0.0.1:5000, then visit the prediction page.

The prediction form stores each demo result in PostgreSQL and shows it in the history page. The UI displays a synthetic-data disclaimer.

## Local setup

```bash
git clone https://github.com/erenjeger/real-estate-estimate.git
cd real-estate-estimate
cp .env.example .env
docker compose up -d db
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
python -m training.train_model
flask --app app run --debug
```

Open http://127.0.0.1:5000.

## Docker

For the web container, set `DATABASE_URL` in `.env` to use hostname `db`:

```text
DATABASE_URL=postgresql+psycopg://homeprice:homeprice_dev@db:5432/homeprice
```

Then:

```bash
docker compose run --rm web flask --app app init-db
docker compose run --rm web python -m training.train_model
docker compose up --build
```

## Database tables
- `predictions`: submitted features and prediction results
- `model_metrics`: evaluation metric schema
- `dataset_sources`: data source provenance

## Research warning

A model trained on synthetic formula-generated data mainly learns that formula. It is useful for UI and integration demos only. For research conclusions about Indonesian housing prices, replace the synthetic data with documented, licensed real data, audit geographic coverage and price definitions, and evaluate with leakage-resistant splits (for example, grouped by housing project where appropriate).

## Tests

```bash
pytest -q
```
