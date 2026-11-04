-- Upgrade the predictions table from the original schema to the demo
-- model schema. Safe to run more than once; existing prediction rows are kept.
BEGIN;

ALTER TABLE predictions
    ADD COLUMN IF NOT EXISTS district_area
        VARCHAR(100) NOT NULL DEFAULT 'Kawasan Perumahan',
    ADD COLUMN IF NOT EXISTS property_type
        VARCHAR(100) NOT NULL DEFAULT 'Rumah Tapak',
    ADD COLUMN IF NOT EXISTS building_age_years
        INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS certificate_type
        VARCHAR(50) NOT NULL DEFAULT 'SHM',
    ADD COLUMN IF NOT EXISTS property_condition
        VARCHAR(80) NOT NULL DEFAULT 'Baik';

COMMIT;
