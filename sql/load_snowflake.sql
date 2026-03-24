-- =============================================================================
-- Snowflake Data Loading Script
-- Pharma Commercial Analytics Dashboard
--
-- Prerequisites:
--   1. A Snowflake account with SYSADMIN or equivalent role
--   2. SnowSQL CLI installed, or run this in a Snowflake worksheet
--   3. CSV files from data/ uploaded to a Snowflake stage
--
-- Run order: this file top to bottom.
-- =============================================================================

-- Step 1: Create database and schema
-- Adjust names to match your org's naming conventions.
CREATE DATABASE IF NOT EXISTS PHARMA_ANALYTICS;
USE DATABASE PHARMA_ANALYTICS;

CREATE SCHEMA IF NOT EXISTS RAW;
USE SCHEMA RAW;

CREATE WAREHOUSE IF NOT EXISTS PHARMA_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

USE WAREHOUSE PHARMA_WH;

-- Step 2: Create tables (from schema.sql)
CREATE OR REPLACE TABLE dim_patients (
    patient_id       VARCHAR PRIMARY KEY,
    age              INTEGER,
    gender           VARCHAR
);

CREATE OR REPLACE TABLE dim_payers (
    payer_id         VARCHAR PRIMARY KEY,
    payer_name       VARCHAR
);

CREATE OR REPLACE TABLE dim_pharmacies (
    pharmacy_id      VARCHAR PRIMARY KEY,
    pharmacy_name    VARCHAR,
    channel_type     VARCHAR
);

CREATE OR REPLACE TABLE dim_drugs (
    drug_id          VARCHAR PRIMARY KEY,
    drug_name        VARCHAR,
    therapeutic_class VARCHAR
);

CREATE OR REPLACE TABLE dim_dates (
    date_key         INTEGER PRIMARY KEY,
    date             DATE,
    year             INTEGER,
    quarter          INTEGER,
    month            INTEGER,
    day              INTEGER,
    day_of_week      VARCHAR
);

CREATE OR REPLACE TABLE fact_rx_fills (
    rx_fill_id           VARCHAR PRIMARY KEY,
    patient_id           VARCHAR REFERENCES dim_patients(patient_id),
    drug_id              VARCHAR REFERENCES dim_drugs(drug_id),
    payer_id             VARCHAR REFERENCES dim_payers(payer_id),
    pharmacy_id          VARCHAR REFERENCES dim_pharmacies(pharmacy_id),
    prescription_date    DATE,
    fill_date            DATE,
    quantity             INTEGER,
    cost                 DECIMAL(12,2),
    time_to_fill_days    INTEGER,
    prior_auth_required  BOOLEAN,
    prior_auth_status    VARCHAR,
    channel_type         VARCHAR,
    is_new_start         BOOLEAN
);

CREATE OR REPLACE TABLE fact_shipments (
    shipment_id     INTEGER AUTOINCREMENT PRIMARY KEY,
    drug_id         VARCHAR REFERENCES dim_drugs(drug_id),
    shipment_month  DATE,
    channel_type    VARCHAR,
    shipments       INTEGER
);

-- Step 3: Create a file format for CSV loading
CREATE OR REPLACE FILE FORMAT csv_format
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL')
    TRIM_SPACE = TRUE;

-- Step 4: Create an internal stage
-- You can also use an external stage (S3, GCS, Azure) if preferred.
CREATE OR REPLACE STAGE pharma_stage
    FILE_FORMAT = csv_format;

-- Step 5: Upload CSV files to the stage
-- Run these from SnowSQL CLI (not from a worksheet):
--
--   snowsql -a <account> -u <user> -d PHARMA_ANALYTICS -s RAW
--
--   PUT file://./data/dim_patients.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/dim_payers.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/dim_pharmacies.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/dim_drugs.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/dim_dates.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/fact_rx_fills.csv @pharma_stage AUTO_COMPRESS=TRUE;
--   PUT file://./data/fact_shipments.csv @pharma_stage AUTO_COMPRESS=TRUE;

-- Step 6: COPY INTO tables
-- Load dimensions first, then facts (referential integrity order).

COPY INTO dim_patients FROM @pharma_stage/dim_patients.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

COPY INTO dim_payers FROM @pharma_stage/dim_payers.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

COPY INTO dim_pharmacies FROM @pharma_stage/dim_pharmacies.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

COPY INTO dim_drugs FROM @pharma_stage/dim_drugs.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

COPY INTO dim_dates FROM @pharma_stage/dim_dates.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

COPY INTO fact_rx_fills FROM @pharma_stage/fact_rx_fills.csv.gz
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

-- fact_shipments has an AUTOINCREMENT PK, so we skip the first column on load
-- and let Snowflake generate it. We load only the 4 data columns.
COPY INTO fact_shipments (drug_id, shipment_month, channel_type, shipments)
    FROM (
        SELECT $1, $2, $3, $4
        FROM @pharma_stage/fact_shipments.csv.gz
    )
    FILE_FORMAT = csv_format
    ON_ERROR = 'ABORT_STATEMENT';

-- Step 7: Validate row counts
-- Expected: 500 patients, 5 payers, 10 pharmacies, 5 drugs, 731 dates, 3000 fills, 240 shipments
SELECT 'dim_patients' AS tbl, COUNT(*) AS rows FROM dim_patients
UNION ALL SELECT 'dim_payers', COUNT(*) FROM dim_payers
UNION ALL SELECT 'dim_pharmacies', COUNT(*) FROM dim_pharmacies
UNION ALL SELECT 'dim_drugs', COUNT(*) FROM dim_drugs
UNION ALL SELECT 'dim_dates', COUNT(*) FROM dim_dates
UNION ALL SELECT 'fact_rx_fills', COUNT(*) FROM fact_rx_fills
UNION ALL SELECT 'fact_shipments', COUNT(*) FROM fact_shipments
ORDER BY tbl;

-- Step 8: Quick integrity checks
-- Orphan check: fills with no matching patient
SELECT COUNT(*) AS orphan_fills
FROM fact_rx_fills f
LEFT JOIN dim_patients p ON f.patient_id = p.patient_id
WHERE p.patient_id IS NULL;

-- Orphan check: fills with no matching payer
SELECT COUNT(*) AS orphan_payer_fills
FROM fact_rx_fills f
LEFT JOIN dim_payers py ON f.payer_id = py.payer_id
WHERE py.payer_id IS NULL;

-- Date range check
SELECT MIN(fill_date) AS earliest_fill, MAX(fill_date) AS latest_fill
FROM fact_rx_fills;

-- Done. Run analysis_queries.sql next.
