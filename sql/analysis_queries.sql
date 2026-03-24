-- SQL queries for analytics on the pharma commercial dashboard.
-- Products: Santyl, Regranex, Silvadene, Remicade, Solu-Medrol
-- Therapeutic areas: wound care, burn care, hyperbaric, infusion therapy

/*
1. Rolling Rx volume trends
   Compute monthly prescription fill counts and a three‑month rolling average
   to highlight volume trends over time.  The window function calculates
   the average of the current and two prior months.
*/

WITH monthly_fills AS (
    SELECT
        date_trunc('month', fill_date) AS month,
        COUNT(*) AS fills
    FROM fact_rx_fills
    GROUP BY 1
)
SELECT
    month,
    fills,
    ROUND(AVG(fills) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3_month_avg
FROM monthly_fills
ORDER BY month;

/*
2. Time‑to‑fill analysis
   Evaluate how long patients wait between prescription and fill.  This query
   computes the average and median time to fill by payer and quarter.  The
   PERCENTILE_CONT window function derives the median within each group.
*/

WITH fills AS (
    SELECT
        payer_id,
        date_trunc('quarter', prescription_date) AS quarter,
        time_to_fill_days
    FROM fact_rx_fills
)
SELECT
    payer_id,
    quarter,
    AVG(time_to_fill_days) AS avg_days_to_fill,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY time_to_fill_days) AS median_days_to_fill
FROM fills
GROUP BY payer_id, quarter
ORDER BY payer_id, quarter;

/*
3. Reimbursement approval rate by payer
   For fills requiring prior authorization, calculate the approval rate.
   We treat 'Approved' vs 'Denied' statuses and compute the percentage of
   approvals per payer.  A window function adds cumulative approval counts
   over time (useful for trending dashboards).
*/

WITH pa AS (
    SELECT
        payer_id,
        fill_date,
        CASE WHEN prior_auth_status = 'Approved' THEN 1 ELSE 0 END AS approved_flag
    FROM fact_rx_fills
    WHERE prior_auth_required = TRUE
)
SELECT
    payer_id,
    DATE_TRUNC('month', fill_date) AS month,
    SUM(approved_flag) AS approvals,
    COUNT(*) AS total_requests,
    ROUND(SUM(approved_flag)::DECIMAL / COUNT(*), 4) AS approval_rate,
    SUM(approved_flag) OVER (PARTITION BY payer_id ORDER BY DATE_TRUNC('month', fill_date)) AS cumulative_approvals,
    COUNT(*) OVER (PARTITION BY payer_id ORDER BY DATE_TRUNC('month', fill_date)) AS cumulative_requests
FROM pa
GROUP BY payer_id, DATE_TRUNC('month', fill_date)
ORDER BY payer_id, month;

/*
4. Channel mix (specialty vs retail) by month
   Determine the distribution of fills through specialty and retail pharmacies.
   The window function calculates the monthly share of each channel.
*/

WITH channel_counts AS (
    SELECT
        date_trunc('month', fill_date) AS month,
        channel_type,
        COUNT(*) AS fills
    FROM fact_rx_fills
    GROUP BY 1,2
)
SELECT
    month,
    channel_type,
    fills,
    ROUND(fills * 100.0 / SUM(fills) OVER (PARTITION BY month), 2) AS channel_share_percentage
FROM channel_counts
ORDER BY month, channel_type;

/*
5. New patient start funnel
   Map a simple patient journey: diagnosis (proxy by first prescription),
   prior authorization approval, first fill, and ongoing therapy.  This query
   produces counts at each stage to support funnel visualization.
*/

WITH
first_prescriptions AS (
    -- First prescription (diagnosis) per patient and drug
    SELECT DISTINCT patient_id, drug_id
    FROM fact_rx_fills
    WHERE is_new_start = TRUE
),
pa_approvals AS (
    -- Patients whose first fill required and received prior authorization
    SELECT DISTINCT f.patient_id, f.drug_id
    FROM fact_rx_fills f
    JOIN first_prescriptions fp ON fp.patient_id = f.patient_id AND fp.drug_id = f.drug_id
    WHERE f.prior_auth_required = TRUE AND f.prior_auth_status = 'Approved'
),
first_fills AS (
    -- Patients who actually filled the first prescription
    SELECT DISTINCT patient_id, drug_id
    FROM fact_rx_fills
    WHERE is_new_start = TRUE
),
ongoing_therapy AS (
    -- Patients with more than one fill (ongoing therapy)
    SELECT patient_id, drug_id
    FROM fact_rx_fills
    GROUP BY patient_id, drug_id
    HAVING COUNT(*) > 1
)
SELECT
    'Diagnosis' AS stage,
    COUNT(*) AS patients
FROM first_prescriptions
UNION ALL
SELECT 'PA Approved' AS stage, COUNT(*) FROM pa_approvals
UNION ALL
SELECT 'First Fill' AS stage, COUNT(*) FROM first_fills
UNION ALL
SELECT 'Ongoing Therapy' AS stage, COUNT(*) FROM ongoing_therapy;