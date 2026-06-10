"""
generate_data.py
Generates a realistic 50,000-row synthetic banking campaign dataset.
Run from project root:  python data/generate_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os, sys

np.random.seed(42)
random.seed(42)

# ── constants ─────────────────────────────────────────────────────────────────
N          = 50_000
CAMPAIGNS  = ['Credit Card Upgrade', 'Personal Loan', 'Savings Account',
              'Wealth Advisory', 'Insurance Cross-Sell']
CHANNELS   = ['Email', 'SMS', 'Mobile App', 'Call Center']
SEGMENTS   = ['Retail', 'Premier', 'Student', 'Salary', 'Mass Affluent']
VARIANTS   = ['A', 'B']
START_DATE = datetime(2024, 6, 1)

# open-rate lookup: (channel, segment) → base probability
OPEN_RATES = {
    ('Email','Retail'):0.26,        ('Email','Premier'):0.43,
    ('Email','Student'):0.20,       ('Email','Salary'):0.29,
    ('Email','Mass Affluent'):0.46,
    ('SMS','Retail'):0.18,          ('SMS','Premier'):0.29,
    ('SMS','Student'):0.14,         ('SMS','Salary'):0.20,
    ('SMS','Mass Affluent'):0.33,
    ('Mobile App','Retail'):0.14,   ('Mobile App','Premier'):0.25,
    ('Mobile App','Student'):0.17,  ('Mobile App','Salary'):0.16,
    ('Mobile App','Mass Affluent'):0.27,
    ('Call Center','Retail'):0.36,  ('Call Center','Premier'):0.54,
    ('Call Center','Student'):0.28, ('Call Center','Salary'):0.39,
    ('Call Center','Mass Affluent'):0.58,
}

# base conversion rate per campaign (applied after respond stage)
CONV_BASE = {
    'Credit Card Upgrade': 0.055, 'Personal Loan': 0.050,
    'Savings Account':     0.030, 'Wealth Advisory': 0.085,
    'Insurance Cross-Sell':0.038,
}

# segment multiplier on conversion
SEG_BOOST = {
    'Premier':1.45, 'Mass Affluent':1.35, 'Salary':1.10,
    'Retail':1.00,  'Student':0.72,
}

# average revenue per conversion by campaign
REV_BASE = {
    'Credit Card Upgrade': 260, 'Personal Loan': 1_550,
    'Savings Account':      55, 'Wealth Advisory': 820,
    'Insurance Cross-Sell': 410,
}

# channel cost per contact
CHAN_COST = {
    'Email': 0.15, 'SMS': 0.08, 'Mobile App': 0.12, 'Call Center': 2.50,
}

# ── build base dataframe ──────────────────────────────────────────────────────
df = pd.DataFrame({
    'customer_id':     np.arange(1, N + 1),
    'campaign':        np.random.choice(CAMPAIGNS, N, p=[0.22,0.20,0.18,0.25,0.15]),
    'channel':         np.random.choice(CHANNELS,  N, p=[0.40,0.25,0.20,0.15]),
    'segment':         np.random.choice(SEGMENTS,  N, p=[0.35,0.25,0.15,0.15,0.10]),
    'variant':         np.random.choice(VARIANTS,  N, p=[0.50,0.50]),
    'age':             np.clip(np.random.normal(42, 14, N).astype(int), 18, 75),
    'tenure_months':   np.clip(np.random.exponential(55, N).astype(int), 1, 240),
    'monthly_balance': np.clip(
                           np.random.lognormal(10, 1.4, N).astype(int),
                           5_000, 5_000_000),
})

df['sent_date'] = [
    START_DATE + timedelta(days=int(x))
    for x in np.random.randint(0, 365, N)
]

# ── simulate engagement (vectorised-friendly loop) ────────────────────────────
bal_mean = df['monthly_balance'].mean()
bal_std  = df['monthly_balance'].std()
bal_max  = float(df['monthly_balance'].max())

opened_l = []; clicked_l = []; responded_l = []; converted_l = []

for row in df.itertuples(index=False):
    # balance & variant adjustment
    bal_adj = 1.0 + float(np.clip((row.monthly_balance - bal_mean) / bal_std * 0.10, -0.30, 0.40))
    var_adj = 1.06 if row.variant == 'B' else 1.0

    p_open = min(0.65, OPEN_RATES.get((row.channel, row.segment), 0.25) * bal_adj * var_adj)
    p_click    = 0.38 + row.monthly_balance / bal_max * 0.28
    p_respond  = 0.52 + row.tenure_months   / 240    * 0.26
    p_convert  = CONV_BASE[row.campaign] * SEG_BOOST[row.segment]

    o = int(random.random() < p_open)
    c = int(o and random.random() < p_click)
    r = int(c and random.random() < p_respond)
    k = int(r and random.random() < p_convert)

    opened_l.append(o); clicked_l.append(c)
    responded_l.append(r); converted_l.append(k)

df['opened']    = opened_l
df['clicked']   = clicked_l
df['responded'] = responded_l
df['converted'] = converted_l

# ── financials ────────────────────────────────────────────────────────────────
df['campaign_cost'] = (
    df['channel'].map(CHAN_COST) + np.random.uniform(0.04, 0.22, N)
).round(2)

revenues = []
for row in df.itertuples(index=False):
    if row.converted:
        bm  = row.monthly_balance / bal_mean
        rev = max(0.0, REV_BASE[row.campaign] * bm * float(np.random.normal(0.92, 0.18)))
        revenues.append(round(rev, 2))
    elif row.clicked and random.random() < 0.018:
        revenues.append(round(float(np.random.uniform(8, 90)), 2))
    else:
        revenues.append(0.0)

df['revenue']   = revenues
df['sent_date'] = df['sent_date'].dt.strftime('%Y-%m-%d')

# ── save ──────────────────────────────────────────────────────────────────────
COLS = ['customer_id','segment','campaign','channel','variant','sent_date',
        'opened','clicked','responded','converted',
        'campaign_cost','revenue','age','tenure_months','monthly_balance']

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campaign_data.csv')
df[COLS].to_csv(out_path, index=False)

print(f"✓  campaign_data.csv  →  {out_path}")
print(f"   Rows            : {N:,}")
print(f"   Conversion rate : {df['converted'].mean():.2%}")
print(f"   Total revenue   : ₹{df['revenue'].sum():,.0f}")
print(f"   Total cost      : ₹{df['campaign_cost'].sum():,.0f}")
roi = (df['revenue'].sum() - df['campaign_cost'].sum()) / df['campaign_cost'].sum()
print(f"   Overall ROI     : {roi:.1%}")
