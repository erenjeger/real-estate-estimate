# Real Estate Estimate

A web application for estimating Indonesian residential property prices using Multiple Linear Regression.

## Tech stack

- Python + Flask
- PostgreSQL
- SQLAlchemy + Flask-Migrate
- Bootstrap 5
- scikit-learn (model integration scaffold)

## Quick start

1. Copy environment file:

   ```bash
   cp .env.example .env
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d db
   ```

3. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   # Windows: .venv\\Scripts\\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Initialize database schema:

   ```bash
   flask --app app db upgrade
   ```

5. Start the application:

   ```bash
   flask --app app run --debug
   ```

Open http://127.0.0.1:5000.

## Configuration

Set `DATABASE_URL` in `.env`. Example:

```text
postgresql+psycopg://homeprice:homeprice_dev@localhost:5432/homeprice
```

Never commit real credentials or production secrets.

## Project status

Initial application foundation. Dataset audit, feature engineering, model training, evaluation, and inference will be added in subsequent steps. No model performance is claimed until trained and evaluated on a validated dataset.
