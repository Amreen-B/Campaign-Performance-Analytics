/* ============================================================
   HSBC Banking Campaign Analytics — SQL Queries
   Compatible with: BigQuery · PostgreSQL · MySQL · Redshift
   ============================================================ */


/* ──────────────────────────────────────────────────────────
   SECTION 1 · CAMPAIGN PERFORMANCE KPIs
   ────────────────────────────────────────────────────────── */

-- 1a. Full campaign KPI table (open rate, CTR, conversion, ROI)
SELECT
    campaign,
    COUNT(*)                                                        AS sent,
    SUM(opened)                                                     AS opened,
    ROUND(SUM(opened)    / COUNT(*) * 100, 2)                      AS open_rate_pct,
    SUM(clicked)                                                    AS clicked,
    ROUND(SUM(clicked)   / NULLIF(SUM(opened),    0) * 100, 2)    AS ctr_pct,
    SUM(responded)                                                  AS responded,
    ROUND(SUM(responded) / NULLIF(SUM(clicked),   0) * 100, 2)    AS response_rate_pct,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND(SUM(campaign_cost), 2)                                    AS total_cost,
    ROUND(SUM(revenue), 2)                                          AS total_revenue,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct,
    ROUND(SUM(campaign_cost)
          / NULLIF(SUM(converted), 0), 2)                          AS cost_per_acq
FROM campaign_data
GROUP BY campaign
ORDER BY roi_pct DESC;


-- 1b. Weekly campaign trend (useful for Power BI time-series chart)
SELECT
    DATE_TRUNC('week', sent_date)                                   AS week_start,
    campaign,
    COUNT(*)                                                        AS sent,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND(SUM(revenue), 2)                                          AS revenue,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct
FROM campaign_data
GROUP BY 1, 2
ORDER BY 1 DESC, roi_pct DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 2 · CUSTOMER SEGMENTATION
   ────────────────────────────────────────────────────────── */

-- 2a. Segment KPIs
SELECT
    segment,
    COUNT(*)                                                        AS sent,
    COUNT(DISTINCT customer_id)                                     AS unique_customers,
    ROUND(SUM(opened)    / COUNT(*) * 100, 2)                      AS open_rate_pct,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND(SUM(revenue), 2)                                          AS total_revenue,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2)           AS revenue_per_customer,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct
FROM campaign_data
GROUP BY segment
ORDER BY roi_pct DESC;


-- 2b. Segment × Campaign conversion heatmap source
SELECT
    segment,
    campaign,
    COUNT(*)                                                        AS sent,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND(SUM(revenue), 2)                                          AS revenue,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct
FROM campaign_data
GROUP BY 1, 2
ORDER BY 1, roi_pct DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 3 · CHANNEL ANALYTICS
   ────────────────────────────────────────────────────────── */

-- 3a. Channel performance comparison
SELECT
    channel,
    COUNT(*)                                                        AS sent,
    ROUND(SUM(opened)    / COUNT(*) * 100, 2)                      AS open_rate_pct,
    ROUND(SUM(clicked)   / NULLIF(SUM(opened), 0) * 100, 2)       AS ctr_pct,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND(SUM(campaign_cost), 2)                                    AS total_cost,
    ROUND(SUM(revenue), 2)                                          AS total_revenue,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct,
    ROUND(SUM(campaign_cost)
          / NULLIF(SUM(converted), 0), 2)                          AS cost_per_acq
FROM campaign_data
GROUP BY channel
ORDER BY roi_pct DESC;


-- 3b. Budget reallocation recommendation
SELECT
    channel,
    ROUND(SUM(campaign_cost), 2)                                    AS current_spend,
    ROUND(SUM(campaign_cost)
          / SUM(SUM(campaign_cost)) OVER () * 100, 1)              AS spend_share_pct,
    SUM(converted)                                                  AS conversions,
    ROUND(SUM(campaign_cost) / NULLIF(SUM(converted), 0), 2)       AS cost_per_acq,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct,
    CASE
        WHEN (SUM(revenue) - SUM(campaign_cost))
             / NULLIF(SUM(campaign_cost), 0) * 100
             > AVG((SUM(revenue) - SUM(campaign_cost))
                   / NULLIF(SUM(campaign_cost), 0) * 100)
             OVER ()
        THEN 'INCREASE BUDGET'
        ELSE 'REDUCE BUDGET'
    END                                                             AS recommendation
FROM campaign_data
GROUP BY channel
ORDER BY roi_pct DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 4 · A/B TESTING
   ────────────────────────────────────────────────────────── */

-- 4a. Variant comparison per campaign (input for chi-square)
SELECT
    campaign,
    variant,
    COUNT(*)                                                        AS sent,
    SUM(opened)                                                     AS opened,
    ROUND(SUM(opened)    / COUNT(*) * 100, 3)                      AS open_rate_pct,
    SUM(clicked)                                                    AS clicked,
    ROUND(SUM(clicked)   / NULLIF(SUM(opened), 0) * 100, 3)       AS ctr_pct,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 4)                      AS conv_rate_pct,
    ROUND(SUM(revenue), 2)                                          AS total_revenue,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct
FROM campaign_data
GROUP BY 1, 2
ORDER BY 1, 2;


-- 4b. Pivot: A vs B side-by-side for each campaign
SELECT
    campaign,
    SUM(CASE WHEN variant='A' THEN 1          ELSE 0 END)          AS sent_A,
    SUM(CASE WHEN variant='A' AND converted=1
                                THEN 1        ELSE 0 END)          AS conv_A,
    ROUND(SUM(CASE WHEN variant='A' AND converted=1
                                THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN variant='A'
                            THEN 1 ELSE 0 END), 0) * 100, 4)      AS conv_rate_A,
    SUM(CASE WHEN variant='B' THEN 1          ELSE 0 END)          AS sent_B,
    SUM(CASE WHEN variant='B' AND converted=1
                                THEN 1        ELSE 0 END)          AS conv_B,
    ROUND(SUM(CASE WHEN variant='B' AND converted=1
                                THEN 1 ELSE 0 END)
          / NULLIF(SUM(CASE WHEN variant='B'
                            THEN 1 ELSE 0 END), 0) * 100, 4)      AS conv_rate_B
FROM campaign_data
GROUP BY campaign
ORDER BY campaign;


/* ──────────────────────────────────────────────────────────
   SECTION 5 · CONVERSION FUNNEL
   ────────────────────────────────────────────────────────── */

-- 5a. Overall funnel stages
SELECT
    COUNT(*)                                    AS sent,
    SUM(opened)                                 AS opened,
    SUM(clicked)                                AS clicked,
    SUM(responded)                              AS responded,
    SUM(converted)                              AS converted,
    ROUND(SUM(opened)    / COUNT(*) * 100, 2)  AS pct_opened,
    ROUND(SUM(clicked)   / COUNT(*) * 100, 2)  AS pct_clicked,
    ROUND(SUM(responded) / COUNT(*) * 100, 2)  AS pct_responded,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)  AS pct_converted
FROM campaign_data;


-- 5b. Funnel by segment (drop-off analysis)
SELECT
    segment,
    COUNT(*)                                                        AS sent,
    SUM(opened)                                                     AS opened,
    ROUND((COUNT(*) - SUM(opened))
          / COUNT(*) * 100, 1)                                     AS drop_at_open_pct,
    SUM(clicked)                                                    AS clicked,
    ROUND((SUM(opened) - SUM(clicked))
          / NULLIF(SUM(opened), 0) * 100, 1)                       AS drop_at_click_pct,
    SUM(responded)                                                  AS responded,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS end_conv_rate_pct
FROM campaign_data
GROUP BY segment
ORDER BY end_conv_rate_pct DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 6 · RFM SEGMENTATION
   ────────────────────────────────────────────────────────── */

-- 6a. RFM scores per customer (use NTILE in BigQuery / window functions)
WITH customer_rfm AS (
    SELECT
        customer_id,
        DATEDIFF(DAY,  MAX(sent_date), CURRENT_DATE)           AS recency_days,
        COUNT(*)                                                AS frequency,
        SUM(revenue)                                            AS monetary
    FROM campaign_data
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT
        customer_id, recency_days, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC)             AS R,
        NTILE(5) OVER (ORDER BY frequency)                     AS F,
        NTILE(5) OVER (ORDER BY monetary)                      AS M
    FROM customer_rfm
)
SELECT
    customer_id, recency_days, frequency, ROUND(monetary, 2) AS monetary,
    R, F, M,
    R + F + M                                                  AS rfm_total,
    CASE
        WHEN R+F+M >= 13 THEN 'Champions'
        WHEN R+F+M >= 11 THEN 'Loyal'
        WHEN R+F+M >=  9 THEN 'Potential'
        WHEN R+F+M >=  7 THEN 'At Risk'
        ELSE 'Need Attention'
    END                                                        AS rfm_tier
FROM rfm_scored
ORDER BY rfm_total DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 7 · CUSTOMER LIFETIME VALUE
   ────────────────────────────────────────────────────────── */

-- 7a. CLV per customer
SELECT
    customer_id,
    segment,
    MAX(tenure_months)                                              AS tenure_months,
    MAX(monthly_balance)                                            AS monthly_balance,
    SUM(revenue)                                                    AS lifetime_revenue,
    ROUND(SUM(revenue)
          / NULLIF(MAX(tenure_months), 0), 4)                      AS monthly_value,
    ROUND(SUM(revenue)
          / NULLIF(MAX(tenure_months), 0)
          * MAX(tenure_months), 2)                                  AS clv
FROM campaign_data
GROUP BY 1, 2
ORDER BY clv DESC;


-- 7b. Segment-level CLV summary
SELECT
    segment,
    COUNT(DISTINCT customer_id)                                     AS customers,
    ROUND(AVG(tenure_months), 1)                                    AS avg_tenure_months,
    ROUND(AVG(monthly_balance), 0)                                  AS avg_balance,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2)           AS avg_revenue_per_cust,
    ROUND(
        AVG(
            SUM(revenue) OVER (PARTITION BY customer_id)
            / NULLIF(MAX(tenure_months) OVER (PARTITION BY customer_id), 0)
            * MAX(tenure_months) OVER (PARTITION BY customer_id)
        ), 2
    )                                                               AS avg_clv
FROM campaign_data
GROUP BY segment
ORDER BY avg_clv DESC;


/* ──────────────────────────────────────────────────────────
   SECTION 8 · COHORT ANALYSIS
   ────────────────────────────────────────────────────────── */

-- 8a. Cohort by account opening year
WITH cohort_base AS (
    SELECT
        customer_id,
        YEAR(sent_date) - FLOOR(tenure_months / 12)                AS cohort_year,
        converted,
        revenue
    FROM campaign_data
)
SELECT
    cohort_year,
    COUNT(DISTINCT customer_id)                                     AS customers,
    SUM(converted)                                                  AS conversions,
    ROUND(SUM(converted) / COUNT(DISTINCT customer_id) * 100, 3)  AS conv_rate_pct,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2)           AS rev_per_customer
FROM cohort_base
WHERE cohort_year BETWEEN 2015 AND 2025
GROUP BY cohort_year
ORDER BY cohort_year;


/* ──────────────────────────────────────────────────────────
   SECTION 9 · OPTIMISATION QUERIES
   ────────────────────────────────────────────────────────── */

-- 9a. Top 10 worst-performing campaign × channel combos (min 50 records)
SELECT
    campaign, channel,
    COUNT(*)                                                        AS sent,
    SUM(converted)                                                  AS converted,
    ROUND(SUM(converted) / COUNT(*) * 100, 3)                      AS conv_rate_pct,
    ROUND((SUM(revenue) - SUM(campaign_cost))
          / NULLIF(SUM(campaign_cost), 0) * 100, 1)                AS roi_pct
FROM campaign_data
GROUP BY 1, 2
HAVING COUNT(*) >= 50
ORDER BY roi_pct ASC
LIMIT 10;


-- 9b. High-CLV customers not yet converted (priority re-targeting)
SELECT
    customer_id,
    segment,
    MAX(monthly_balance)                                            AS balance,
    MAX(tenure_months)                                              AS tenure_months,
    SUM(converted)                                                  AS past_conversions,
    ROUND(SUM(revenue), 2)                                          AS lifetime_revenue
FROM campaign_data
WHERE monthly_balance > 500000
  AND converted = 0
GROUP BY 1, 2
ORDER BY balance DESC
LIMIT 100;


/* ──────────────────────────────────────────────────────────
   PERFORMANCE NOTES
   ──────────────────────────────────────────────────────────
   Recommended indexes:
     CREATE INDEX idx_campaign_date ON campaign_data (campaign, sent_date);
     CREATE INDEX idx_segment_chan  ON campaign_data (segment,  channel);
     CREATE INDEX idx_converted     ON campaign_data (converted);

   For BigQuery: partition by DATE(sent_date); cluster by segment, campaign.
   ────────────────────────────────────────────────────────── */
