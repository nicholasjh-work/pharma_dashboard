# Pharma Commercial Analytics Dashboard

**[Live Demo](https://nicholasjh-work.github.io/pharma_dashboard/)**

Simulates a commercial analytics workflow for specialty pharmaceutical products used in wound care, burn care, hyperbaric, and infusion therapy. Uses synthetic data to model prescription fills, new patient starts, prior authorization outcomes, channel mix (specialty vs. retail pharmacies), and demand shipments.

Built with Snowflake, SQL (window functions, CTEs), Power BI, and Python (pandas, matplotlib, seaborn).

## Business Context

Manufacturers of specialty drugs track more than total prescription volume. Key performance indicators include:

- **New patient starts:** patients initiating therapy, an early indicator of demand and launch effectiveness.
- **Prior authorization approval/denial rates:** high denial rates signal access barriers requiring payer outreach or patient support.
- **Time to fill:** delays between prescription and fill reduce adherence and signal process bottlenecks.
- **Channel mix:** specialty vs. retail pharmacy distribution informs staffing and logistics.
- **Demand shipments:** manufacturer-to-distributor shipments compared against prescription demand for supply chain alignment.

## Repo Structure

```
pharma-analytics/
  data/                          Synthetic CSV files (dims + facts)
    dim_patients.csv             500 patients
    dim_payers.csv               5 payer types
    dim_pharmacies.csv           10 pharmacies (specialty + retail)
    dim_drugs.csv                5 drugs (Santyl, Regranex, Silvadene, Remicade, Solu-Medrol)
    dim_dates.csv                Calendar 2024-2025
    fact_rx_fills.csv            3,000 prescription fill events
    fact_shipments.csv           240 monthly shipment rows
  sql/
    schema.sql                   Snowflake DDL (5 dims, 2 facts)
    analysis_queries.sql         5 analytical queries with window functions
    load_snowflake.sql           Full Snowflake setup: DB, schema, stage, COPY INTO, validation
  notebooks/
    patient_cohort_analysis.ipynb  EDA notebook (pandas, matplotlib, seaborn)
  load_to_snowflake.py           Python loader using snowflake-connector-python
  requirements.txt               Python dependencies
  .env.example                   Snowflake credential template
  .gitignore
  README.md
```

## Data Generation

All data are synthetic. 3,000 Rx fill events between Jan 2024 and Dec 2025 across five products used in wound care, burn care, hyperbaric, and infusion therapy (Santyl, Regranex, Silvadene, Remicade, Solu-Medrol). Each fill includes prescription and fill dates, quantity, cost, prior authorization status, channel type, and a new-start flag.

## Schema Design

Snowflake star schema defined in `sql/schema.sql`:

- **Dimensions:** `dim_patients`, `dim_payers`, `dim_pharmacies`, `dim_drugs`, `dim_dates`
- **Facts:** `fact_rx_fills` (individual prescription events), `fact_shipments` (monthly demand shipments)

Foreign keys are defined for documentation; Snowflake treats these as informational.

## Analytics Queries

`sql/analysis_queries.sql` contains 5 queries demonstrating window functions, date truncation, and conditional aggregation:

1. **Rolling Rx volume trends** with 3-month moving average
2. **Time-to-fill analysis** by payer and quarter (average + median via PERCENTILE_CONT)
3. **Reimbursement approval rate by payer** with cumulative tracking
4. **Channel mix** (specialty vs. retail share per month)
5. **Patient journey funnel** (diagnosis, PA approved, first fill, ongoing therapy)

## Loading Data into Snowflake

**Option A: SnowSQL CLI**

Run `sql/load_snowflake.sql` in order. It creates the database, schema, warehouse, tables, file format, and stage, then loads via COPY INTO with validation.

```bash
snowsql -a <account> -u <user> -d PHARMA_ANALYTICS -s RAW -f sql/load_snowflake.sql
```

For the PUT commands (file upload to stage), run from SnowSQL interactively:

```
PUT file://./data/dim_patients.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/dim_payers.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/dim_pharmacies.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/dim_drugs.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/dim_dates.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/fact_rx_fills.csv @pharma_stage AUTO_COMPRESS=TRUE;
PUT file://./data/fact_shipments.csv @pharma_stage AUTO_COMPRESS=TRUE;
```

**Option B: Python script**

```bash
cp .env.example .env          # fill in Snowflake credentials
pip install -r requirements.txt
python load_to_snowflake.py
```

Uses `snowflake-connector-python` with `write_pandas` for bulk loading. Creates tables from `schema.sql`, loads all CSVs, and validates row counts.

## Power BI Dashboard

The metrics map to a dashboard with these pages:

- **Overview:** KPI cards (total Rx, new starts, approval rate, avg time to fill) with payer/drug slicers
- **Volume trends:** monthly fills with rolling 3-month average, drill-down by channel or drug
- **Patient journey funnel:** diagnosis, PA approved, first fill, ongoing therapy
- **Payer performance:** approval rates and time-to-fill by payer with conditional formatting
- **Channel mix:** stacked column chart showing specialty vs. retail over time
- **Demand vs. supply:** shipments overlaid with Rx fills for inventory alignment

## Python Notebook

`notebooks/patient_cohort_analysis.ipynb` covers:

- Time-to-fill distribution by payer (box plots)
- Channel mix (specialty vs. retail bar charts)
- Prior authorization outcomes
- Average cost per therapeutic class
- Monthly new patient starts over time

## Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/pharma-analytics.git
cd pharma-analytics
pip install -r requirements.txt

# Option A: Load to Snowflake via Python
cp .env.example .env  # fill credentials
python load_to_snowflake.py

# Option B: Load via SnowSQL
snowsql -a <account> -u <user> -f sql/load_snowflake.sql

# Run the notebook
jupyter notebook notebooks/patient_cohort_analysis.ipynb
```

## Disclaimer

Educational and demonstration purposes only. All data are synthetic and do not represent real patients, transactions, or commercial performance.
