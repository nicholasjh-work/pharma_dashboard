-- Snowflake schema definition for the Pharma Commercial Analytics Dashboard

-- Dimension tables

-- Patient dimension stores demographic attributes for each unique patient.
CREATE OR REPLACE TABLE dim_patients (
    patient_id       VARCHAR PRIMARY KEY,
    age              INTEGER,
    gender           VARCHAR
);

-- Payer dimension lists payers such as commercial insurers, Medicare, etc.
CREATE OR REPLACE TABLE dim_payers (
    payer_id         VARCHAR PRIMARY KEY,
    payer_name       VARCHAR
);

-- Pharmacy dimension identifies dispensing channels and stores channel type.
CREATE OR REPLACE TABLE dim_pharmacies (
    pharmacy_id      VARCHAR PRIMARY KEY,
    pharmacy_name    VARCHAR,
    channel_type     VARCHAR
);

-- Drug dimension holds high‑level attributes for each product under study.
CREATE OR REPLACE TABLE dim_drugs (
    drug_id          VARCHAR PRIMARY KEY,
    drug_name        VARCHAR,
    therapeutic_class VARCHAR
);

-- Date dimension simplifies temporal reporting and enables easy date rollups.
CREATE OR REPLACE TABLE dim_dates (
    date_key         INTEGER PRIMARY KEY,
    date             DATE,
    year             INTEGER,
    quarter          INTEGER,
    month            INTEGER,
    day              INTEGER,
    day_of_week      VARCHAR
);

-- Fact table capturing individual prescription fills.  Each row represents
-- one fill for one patient and product and links back to all dimension tables.
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

-- Fact table summarizing monthly demand shipments by product and channel.
CREATE OR REPLACE TABLE fact_shipments (
    shipment_id     INTEGER AUTOINCREMENT PRIMARY KEY,
    drug_id         VARCHAR REFERENCES dim_drugs(drug_id),
    shipment_month  DATE,
    channel_type    VARCHAR,
    shipments       INTEGER
);