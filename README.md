# Banking Marketing Campaign Analytics

> **End-to-end campaign analytics project** — Python · SQL · Power BI  
> Analysing 50,000 campaign contacts across 5 segments, 4 channels, and 5 campaigns.

---

## Skills Demonstrated

Python • SQL • Data Cleaning • EDA • KPI Reporting • Customer Segmentation • A/B Testing • Statistical Analysis • Funnel Analytics • CLV • RFM • Cohort Analysis • Power BI • Business Strategy

---

## Key Results

| KPI | Value |
|---|---|
| Dataset size | 50,000 contacts · 15 features |
| Overall ROI | **397%** |
| Best campaign | Personal Loan — 957% ROI |
| Best segment | Mass Affluent — 0.74% conversion |
| Best channel | Email — 1,325% ROI, INR 66 CPA |
| Funnel efficiency | 0.39% end-to-end conversion |

ROI = (Revenue − Cost) / Cost × 100

---
## Business Impact

This analysis identified several opportunities to improve campaign profitability:

- Reallocate budget toward Personal Loan and Wealth Advisory campaigns.
- Shift low-performing Call Centre spend into Email and SMS channels.
- Target Premier and Mass Affluent customers with premium products.
- Improve subject-line strategy to reduce the largest funnel drop-off stage.

If implemented, these recommendations are expected to improve campaign ROI, reduce customer acquisition costs, and increase conversions through more targeted budget allocation and customer segmentation strategies.

---

## Dashboard Preview

| Executive Summary | Campaign Performance | Customer Segmentation |
|-------------------|----------------------|----------------------|
| ![](dashboards/screenshots/01_executive_summary.png) | ![](dashboards/screenshots/02_campaign_performance.png) | ![](dashboards/screenshots/03_segmentation.png) |

----

## Project Structure

```
Banking-Campaign-Analytics/
│
├── data/
│   ├── campaign_data.csv          # 50,000-row synthetic dataset
│   └── generate_data.py           # Reproducible data generation script
│
├── notebooks/
│   └── Campaign_Analytics.py      # Full 9-section analytics pipeline
│                                  # (EDA → KPIs → Segment → Channel →
│                                  #  A/B Test → Funnel → CLV/RFM → Cohort)
│
├── sql/
│   └── campaign_queries.sql       # Production SQL: all KPIs, RFM, CLV,
│                                  # funnel, A/B pivot, budget reallocation
│
├── dashboards/
│   └── screenshots/               # 9 chart PNGs (ready for Power BI import)
│       ├── 01_executive_summary.png
│       ├── 02_campaign_performance.png
│       ├── 03_segmentation.png
│       ├── 04_channel_analytics.png
│       ├── 05_ab_testing.png
│       ├── 06_funnel_overall.png
│       ├── 06b_funnel_by_segment.png
│       ├── 07_clv_rfm.png
│       └── 08_cohort_analysis.png
│
├── reports/
│   └── Business_Recommendations.md  # 7 findings with projected revenue impact
│
└── docs/
    └── data_dictionary.md           # Column definitions, formulas, dataset stats
```

## Quick Start
```
# Clone repository
git clone https://github.com/your-username/Banking-Campaign-Analytics.git

# Install dependencies
pip install -r requirements.txt

# Run analytics pipeline
python notebooks/Campaign_Analytics.py
```

---

## Analyses Covered

### 1 · Data Load & Quality Validation
Eight automated checks (null counts, funnel logic, range validation). Every run starts clean.

### 2 · Campaign KPI Metrics
Open Rate, CTR, Response Rate, Conversion Rate, ROI, and Cost Per Acquisition for each campaign. Ranked by ROI; identifies best and worst performers.

### 3 · Customer Segmentation
Five segments (Retail, Premier, Student, Salary, Mass Affluent) compared on conversion, revenue, and ROI. Includes a Segment × Campaign heatmap to find the best product-segment pairings.

### 4 · Channel Analytics
Email vs SMS vs Mobile App vs Call Centre — open rate, CTR, conversion rate, ROI, and cost per acquisition. Includes a budget reallocation SQL query.

### 5 · A/B Testing
Chi-square significance test for each campaign variant. Reports rate for A and B, absolute lift, p-value, and a plain-English recommendation.

### 6 · Conversion Funnel
Sent → Opened → Clicked → Responded → Converted with drop-off % at each stage. Repeated by segment to identify which group leaks most.

### 7 · CLV & RFM Segmentation
Customer Lifetime Value (monthly revenue × tenure). RFM scoring (Recency / Frequency / Monetary) with five tiers: Champions, Loyal, Potential, At Risk, Need Attention.

### 8 · Cohort Analysis
Groups customers by account-opening year. Shows how customer vintage affects engagement and conversion — useful for targeting newer vs. established customers differently.

### 9 · Executive KPI Dashboard
Four KPI tiles (Revenue, ROI, Conversion Rate, Total Conversions) saved as a chart for direct use in presentations or Power BI.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Analytics pipeline, data generation |
| Pandas / NumPy | Data manipulation and metrics |
| SciPy | Chi-square A/B significance testing |
| Matplotlib / Seaborn | Chart generation |
| SQL (BigQuery dialect) | Production KPI queries |
| Power BI | Dashboard (see `dashboards/`) |

---

## Dashboard Pages (Power BI)

| Page | Content |
|---|---|
| Executive Summary | 4 KPI tiles: Revenue, ROI, Conversion Rate, Conversions |
| Campaign Performance | ROI, Conversion Rate, Revenue by campaign (bar charts) |
| Customer Segmentation | Segment KPIs + Segment × Campaign heatmap |
| Channel Analytics | Open rate, CTR, ROI, CPA by channel |
| A/B Testing | Variant A vs B conversion comparison with p-values |
| Conversion Funnel | Waterfall funnel + segment-level funnel bars |
| CLV & RFM | CLV by segment + RFM tier pie chart |
| Cohort Analysis | Dual-axis: customer count + conversion rate by cohort year |

Charts for each page are in `dashboards/screenshots/`.

---

## Business Recommendations (Summary)

Full analysis in `reports/Business_Recommendations.md`.

1. **Scale Personal Loan and Wealth Advisory** (best ROI); pause Savings Account (negative ROI).
2. **Prioritise Premier and Mass Affluent** segments — 2–5× higher conversion than Retail.
3. **Shift budget from Call Centre to Email/SMS** for mass campaigns; Call Centre reserved for high-value segments only.
4. **Redesign Variant B** with a materially different offer before concluding A/B test.
5. **Fix the open-stage drop-off** (71%) — subject-line A/B testing is the highest-leverage action.
6. **Create a CLV priority track** for top-20% customers (RFM score ≥ 11).
7. **Build an onboarding journey** for customers in their first 12 months.

---

## License

MIT — free to use, fork, and adapt.
