# Pharma Commercial Analytics Dashboard

This project simulates a commercial analytics workflow for a specialty pharmaceutical product.  It uses synthetic data to model prescription fills, new patient starts, prior authorization outcomes, channel mix (specialty vs. retail pharmacies) and demand shipments.  The goal is to demonstrate how a Snowflake‑style data warehouse, SQL window functions, a Power BI dashboard and a Python notebook can be combined to provide actionable insights for a commercial team.

## Business context

Manufacturers of specialty drugs need to monitor more than just total prescription volume.  Key performance indicators include:

- **New patient starts:** counts of patients initiating therapy provide an early indicator of demand and the effectiveness of launch programs.
- **Prior authorization approval/denial rates:** high denial rates can signal access barriers that require payer outreach or patient support.
- **Time to fill:** delays between prescription and fill can reduce adherence and signal process bottlenecks.
- **Channel mix:** understanding whether prescriptions flow through specialty vs. retail pharmacies helps optimize distribution strategy and patient support staffing.
- **Demand shipments:** shipments from the manufacturer to distributors provide a view of supply chain dynamics and can be compared with prescription demand.

This project constructs a snowflake schema around these metrics, populates it with synthetic data, and demonstrates analytical queries and visualizations that could be used in a real dashboard.

## Data generation

All data in this repository are synthetic and do not represent any actual patients or transactions.  The dataset was generated using the Python script embedded in `data_generation.py`.  Key design choices include:

- **Patients:** 500 fictitious patients with age and gender attributes.
- **Payers:** five payer types (commercial, Medicare, Medicaid, VA and self‑pay).
- **Pharmacies:** ten pharmacies randomly designated as specialty or retail channels.
- **Drugs:** five products across different therapeutic classes.
- **Rx fills:** 3 000 prescription fill events between **1 January 2024** and **31 December 2025**.  Each event includes prescription and fill dates, quantity, cost, prior authorization status and channel type.  A flag identifies whether the event is a new start for the patient.
- **Shipments:** monthly demand shipments by drug and channel.

The generated CSV files live under the `data/` directory:

| File | Description |
| --- | --- |
| `dim_patients.csv` | Patient dimension with IDs, age and gender. |
| `dim_payers.csv` | Payer dimension with payer names. |
| `dim_pharmacies.csv` | Pharmacy dimension with channel type. |
| `dim_drugs.csv` | Drug dimension with therapeutic class. |
| `dim_dates.csv` | Date dimension for each calendar day from 2024–2025. |
| `fact_rx_fills.csv` | Fact table of prescription fills. |
| `fact_shipments.csv` | Fact table of monthly demand shipments. |

## Schema design

The snowflake schema is defined in `schema.sql`.  It comprises five dimension tables and two fact tables:

- `dim_patients`, `dim_payers`, `dim_pharmacies`, `dim_drugs` and `dim_dates` hold descriptive attributes.
- `fact_rx_fills` captures individual prescription events and links back to all dimensions.  It includes measures such as quantity, cost, time to fill, prior authorization status and whether the fill represents a new patient start.
- `fact_shipments` stores monthly shipment volumes by product and channel.

Referential integrity is enforced via foreign keys, although Snowflake treats these as informational rather than enforced constraints.

## Analytics queries

`analysis_queries.sql` contains example SQL for Snowflake (or other ANSI‑SQL warehouse) demonstrating how to derive key metrics:

1. **Rolling Rx volume trends:** calculates monthly fill counts and a three‑month rolling average using window functions to smooth trends.
2. **Time‑to‑fill analysis:** computes the average and median time from prescription to fill for each payer and quarter.
3. **Reimbursement approval rate by payer:** filters fills requiring prior authorization and calculates approval rates and cumulative approvals over time.
4. **Channel mix:** determines the share of fills through specialty vs. retail pharmacies each month.
5. **Patient journey funnel:** counts patients at each stage of a simple funnel (diagnosis, prior authorization approval, first fill and ongoing therapy).

These queries can be executed directly in Snowflake or another SQL environment after loading the CSV files into corresponding tables.  They illustrate common analytical patterns such as window functions (`OVER`, `ROWS BETWEEN`), date truncation and conditional aggregation.

## Power BI dashboard

While the repository cannot include a Power BI `.pbix` file, the metrics above lend themselves to a dashboard with the following structure:

- **Overview page:** big‑number cards showing total prescriptions, new patient starts, approval rate and average time to fill.  A slicer allows filtering by therapeutic class or payer.
- **Volume trends:** line chart showing monthly fills with a rolling three‑month average, with drill‑down by channel type or drug.
- **Patient journey funnel:** funnel visualization displaying counts of patients at each stage (diagnosis → PA approved → first fill → ongoing therapy).
- **Payer performance:** bar charts comparing approval rates and time‑to‑fill statistics across payers, with conditional formatting to highlight outliers.
- **Channel mix:** stacked column chart showing specialty vs. retail fills over time.
- **Demand vs. supply:** combination chart overlaying shipment volumes from `fact_shipments` with prescription fills to highlight inventory alignment.

To build the dashboard:

1. **Import data:** load the CSV files from `data/` into Power BI Desktop and define relationships between fact and dimension tables using the keys defined in `schema.sql`.
2. **Create measures:** implement DAX measures mirroring the SQL queries (e.g., rolling averages, approval rate, time‑to‑fill percentiles).  DAX functions such as `CALCULATE`, `AVERAGEX`, `FILTER` and `DATEADD` will be useful.
3. **Design visuals:** assemble the pages described above, ensuring consistent formatting and slicers for payer, drug and date.
4. **Publish:** deploy the dashboard to Power BI Service (optional) and set up scheduled refreshes if you load updated data.

## Python notebook

`patient_cohort_analysis.ipynb` contains an exploratory data analysis of the synthetic patient cohorts using pandas, seaborn and matplotlib.  It visualizes:

- Time‑to‑fill distribution by payer using box plots.
- Channel mix counts (specialty vs. retail) using bar charts.
- Prior authorization outcomes (approved vs. denied) using bar charts.
- Average cost per therapeutic class.
- Monthly new patient starts over time.

To run the notebook, install the required Python packages (pandas, matplotlib and seaborn) and execute the cells.  The notebook assumes it is run from the repository root so that it can access the `data/` directory relative to its working directory.

## Getting started

1. **Clone or download** this repository.
2. Ensure that Python 3.8+ is installed and install dependencies with `pip install pandas matplotlib seaborn`.
3. Load the CSV data into your data warehouse of choice (e.g., Snowflake, BigQuery) using the table definitions in `schema.sql`.
4. Run the SQL queries in `analysis_queries.sql` to compute KPIs or translate them into DAX measures within Power BI.
5. Explore the synthetic data by opening `patient_cohort_analysis.ipynb` in Jupyter.

## Disclaimer

This project is for educational and demonstration purposes only.  All data are synthetic and randomly generated; they do not reflect real patients or commercial performance.
The analytics code and schema in this repository reflect a project delivered for a healthcare analytics client focused on wound, burn, hyperbaric, and infusion services. The actual data used in that engagement remain confidential and proprietary. The sample data bundled here are synthetic and randomly generated and are not derived from real patients or commercial activity.
