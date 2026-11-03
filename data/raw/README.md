# Demo dataset — Home Price Indonesia

File: `data/raw/home_price_demo_synthetic.csv`

## Important: synthetic data only

This file contains **1,500 generated synthetic records** for UI, database, and ML-pipeline demonstrations. It is not scraped, surveyed, transaction, appraisal, or official Indonesian property-market data. The price values are generated from an illustrative formula with random variation. They must not be interpreted as current market prices or used to make real property decisions.

All rows carry `data_origin=SYNTHETIC_DEMO_ONLY`.

## Geographic coverage

The generator samples from illustrative city/regency labels across Indonesia's provinces. This is a demonstration list, not a statistically representative sample. Some provinces/cities are represented by only one city label and the row counts per city are random.

## Columns

| Column | Type | Description |
|---|---|---|
| record_id | integer | Unique synthetic row identifier |
| province | category | Province label |
| city_regency | category | City/regency label |
| district_area | category | Illustrative area type, not an actual district |
| property_type | category | Illustrative house type |
| land_area_m2 | numeric | Land area in square metres |
| building_area_m2 | numeric | Building area in square metres |
| bedrooms | integer | Bedroom count |
| bathrooms | integer | Bathroom count |
| floors | integer | Number of floors |
| building_age_years | integer | Illustrative building age |
| certificate_type | category | Illustrative certificate category |
| property_condition | category | Illustrative property condition |
| price_idr | integer | Synthetic target price in IDR |
| data_origin | category | Always `SYNTHETIC_DEMO_ONLY` |

## Suggested demo use

1. Preview the dataset in the dashboard or a data table.
2. Test CSV ingestion and PostgreSQL persistence.
3. Demonstrate preprocessing, train/test split, and a baseline Multiple Linear Regression workflow.
4. Demonstrate the prediction form and prediction-history UI.

## Research limitation

Do not report model metrics from this synthetic dataset as evidence of real-world predictive performance. A model trained and tested on generated formula-based values mainly learns the formula used by the generator. Before a research evaluation, replace or supplement this data with a documented, licensed, sufficiently representative real dataset and use a validation strategy that avoids leakage between duplicate or related listings.
