# Data Dictionary — `campaign_data.csv`

| Column | Type | Description | Example |
|---|---|---|---|
| `customer_id` | int | Unique customer identifier | 10042 |
| `segment` | str | Banking segment (Retail / Premier / Student / Salary / Mass Affluent) | Premier |
| `campaign` | str | Campaign name | Wealth Advisory |
| `channel` | str | Delivery channel (Email / SMS / Mobile App / Call Center) | Email |
| `variant` | str | A/B test variant (A = control, B = test) | B |
| `sent_date` | date | Date message was sent (YYYY-MM-DD) | 2024-08-14 |
| `opened` | 0/1 | Customer opened the message | 1 |
| `clicked` | 0/1 | Customer clicked a link (requires opened=1) | 1 |
| `responded` | 0/1 | Customer took next action (requires clicked=1) | 0 |
| `converted` | 0/1 | Customer completed desired action | 0 |
| `campaign_cost` | float | Cost to send this contact (INR) | 0.23 |
| `revenue` | float | Revenue attributed to this contact (INR) | 0.00 |
| `age` | int | Customer age in years (18–75) | 38 |
| `tenure_months` | int | Months as a bank customer (1–240) | 72 |
| `monthly_balance` | int | Average monthly account balance (INR) | 284000 |

## Derived Metrics

| Metric | Formula |
|---|---|
| Open Rate | `SUM(opened) / COUNT(*) × 100` |
| CTR | `SUM(clicked) / SUM(opened) × 100` |
| Response Rate | `SUM(responded) / SUM(clicked) × 100` |
| Conversion Rate | `SUM(converted) / COUNT(*) × 100` |
| ROI | `(SUM(revenue) − SUM(campaign_cost)) / SUM(campaign_cost) × 100` |
| CPA | `SUM(campaign_cost) / SUM(converted)` |
| CLV | `(SUM(revenue) / tenure_months) × tenure_months` |

## Dataset Stats

- **Rows**: 50,000
- **Period**: June 2024 – May 2025
- **Customers**: 50,000 unique
- **Campaigns**: 5
- **Channels**: 4
- **Segments**: 5
