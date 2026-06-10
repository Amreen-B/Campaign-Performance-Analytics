"""
Campaign_Analytics.py  —  HSBC Banking Campaign Analytics
Full pipeline: EDA → KPIs → Segmentation → Channel → A/B Test
              → Funnel → CLV/RFM → Cohort → Executive Summary
Run:  python notebooks/Campaign_Analytics.py
"""

import os, warnings, math
import pandas  as pd
import numpy   as np
import matplotlib.pyplot    as plt
import matplotlib.ticker    as mtick
import seaborn as sns
from scipy import stats

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({'figure.dpi': 130,
                     'axes.spines.top': False, 'axes.spines.right': False})

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA    = os.path.join(ROOT, 'data',       'campaign_data.csv')
SCREENS = os.path.join(ROOT, 'dashboards', 'screenshots')
os.makedirs(SCREENS, exist_ok=True)

def save(fname):
    plt.savefig(os.path.join(SCREENS, fname), bbox_inches='tight', facecolor='white')
    plt.close('all')
    print(f'     saved -> {fname}')

def section(t):
    print(f'\n{"─"*68}\n  {t}\n{"─"*68}')

def safe_qcut(series, q, labels):
    try:
        return pd.qcut(series, q, labels=labels, duplicates='drop').astype(int)
    except ValueError:
        return pd.qcut(series.rank(method='first'), q, labels=labels, duplicates='drop').astype(int)

def build_kpis(frame, group_by):
    g = (frame.groupby(group_by)
               .agg(sent=('customer_id','count'),
                    opened=('opened','sum'),
                    clicked=('clicked','sum'),
                    responded=('responded','sum'),
                    converted=('converted','sum'),
                    cost=('campaign_cost','sum'),
                    revenue=('revenue','sum'))
               .reset_index())
    safe = lambda n: n.replace(0, np.nan)
    g['open_rate'] = (g.opened    / safe(g.sent)      * 100).round(2)
    g['ctr']       = (g.clicked   / safe(g.opened)    * 100).round(2)
    g['resp_rate'] = (g.responded / safe(g.clicked)   * 100).round(2)
    g['conv_rate'] = (g.converted / safe(g.sent)      * 100).round(3)
    g['roi_pct']   = ((g.revenue - g.cost) / safe(g.cost) * 100).round(1)
    g['cpa']       = (g.cost      / safe(g.converted)     ).round(2)
    return g.sort_values('roi_pct', ascending=False).reset_index(drop=True)

# ══════════════════════════
print('='*68)
print('  HSBC  BANKING CAMPAIGN ANALYTICS  —  FULL PIPELINE')
print('='*68)

# ── 1. LOAD & VALIDATE ─────────────────────────────────────────────────────
section('1 · DATA LOAD & QUALITY VALIDATION')
df = pd.read_csv(DATA, parse_dates=['sent_date'])

checks = {
    'No nulls'              : df.isnull().sum().sum() == 0,
    'opened >= clicked'     : (df.opened    >= df.clicked   ).all(),
    'clicked >= responded'  : (df.clicked   >= df.responded ).all(),
    'responded >= converted': (df.responded >= df.converted ).all(),
    'revenue >= 0'          : (df.revenue   >= 0            ).all(),
    'age in [18,75]'        : df.age.between(18, 75).all(),
    'tenure_months > 0'     : (df.tenure_months > 0).all(),
}
for chk, ok in checks.items():
    print(f'  {"OK" if ok else "FAIL"}  {chk}')

print(f'\n  Shape            : {df.shape[0]:,} rows x {df.shape[1]} cols')
print(f'  Date range       : {df.sent_date.min().date()} to {df.sent_date.max().date()}')
print(f'  Unique customers : {df.customer_id.nunique():,}')

# ── 2. CAMPAIGN KPIs ───────────────────────────────────────────────────────
section('2 · CAMPAIGN PERFORMANCE KPIs')
camp = build_kpis(df, 'campaign')
print(camp[['campaign','sent','open_rate','ctr','conv_rate','roi_pct','cpa']].to_string(index=False))
print(f'\n  Best  ROI : {camp.iloc[0].campaign}  ({camp.iloc[0].roi_pct:.1f}%)')
print(f'  Worst ROI : {camp.iloc[-1].campaign}  ({camp.iloc[-1].roi_pct:.1f}%)')

CAMP_PAL = sns.color_palette('Set2', len(camp))
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Campaign Performance Overview', fontsize=14, fontweight='bold', y=1.01)
for ax, col, xlabel, title in zip(
        axes,
        ['roi_pct', 'conv_rate', 'revenue'],
        ['ROI (%)', 'Conversion Rate (%)', 'Revenue (INR 000)'],
        ['ROI by Campaign', 'Conversion Rate by Campaign', 'Revenue by Campaign']):
    vals = camp[col] / (1000 if col == 'revenue' else 1)
    ax.barh(camp.campaign, vals, color=CAMP_PAL)
    ax.set_xlabel(xlabel); ax.set_title(title, fontweight='bold')
    ax.invert_yaxis()
save('02_campaign_performance.png')

# ── 3. SEGMENTATION ────────────────────────────────────────────────────────
section('3 · CUSTOMER SEGMENTATION')
seg = build_kpis(df, 'segment')
seg['rev_per_cust'] = (seg.revenue / seg.sent).round(2)
print(seg[['segment','sent','conv_rate','revenue','roi_pct','rev_per_cust']].to_string(index=False))

SEG_PAL = sns.color_palette('Paired', len(seg))
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle('Customer Segment Analysis', fontsize=14, fontweight='bold', y=1.01)
axes[0].bar(seg.segment, seg.conv_rate, color=SEG_PAL)
axes[0].set_ylabel('Conv Rate (%)'); axes[0].set_title('Conversion Rate by Segment', fontweight='bold')
axes[0].tick_params(axis='x', rotation=15)
axes[1].bar(seg.segment, seg.revenue / 1000, color=SEG_PAL)
axes[1].set_ylabel('Revenue (INR 000)'); axes[1].set_title('Revenue by Segment', fontweight='bold')
axes[1].tick_params(axis='x', rotation=15)
pivot = df.groupby(['segment','campaign'])['converted'].mean().unstack().fillna(0) * 100
sns.heatmap(pivot.round(3), annot=True, fmt='.3f', cmap='YlOrRd',
            linewidths=0.5, ax=axes[2], cbar_kws={'label':'Conv Rate (%)'})
axes[2].set_title('Conv Rate: Segment x Campaign', fontweight='bold')
axes[2].tick_params(axis='x', rotation=20)
save('03_segmentation.png')

# ── 4. CHANNEL ANALYTICS ──────────────────────────────────────────────────
section('4 · CHANNEL ANALYTICS')
chan = build_kpis(df, 'channel')
print(chan[['channel','sent','open_rate','ctr','conv_rate','roi_pct','cpa']].to_string(index=False))

CHAN_PAL = sns.color_palette('coolwarm', len(chan))
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle('Channel Performance Dashboard', fontsize=14, fontweight='bold', y=1.01)
for ax, col, ylabel, title in zip(
        axes,
        ['open_rate', 'conv_rate', 'roi_pct'],
        ['Open Rate (%)', 'Conversion Rate (%)', 'ROI (%)'],
        ['Open Rate by Channel', 'Conv Rate by Channel', 'ROI by Channel']):
    ax.bar(chan.channel, chan[col], color=CHAN_PAL)
    ax.set_ylabel(ylabel); ax.set_title(title, fontweight='bold')
    ax.tick_params(axis='x', rotation=10)
save('04_channel_analytics.png')

# ── 5. A/B TESTING ────────────────────────────────────────────────────────
section('5 · A/B TESTING  (Chi-Square + Lift)')
records = []
for cname in df.campaign.unique():
    for metric, label in [('opened','Open Rate'),('clicked','CTR'),('converted','Conv Rate')]:
        a = df[(df.campaign == cname) & (df.variant == 'A')]
        b = df[(df.campaign == cname) & (df.variant == 'B')]
        ct = [[a[metric].sum(), len(a)-a[metric].sum()],
              [b[metric].sum(), len(b)-b[metric].sum()]]
        _, p, _, _ = stats.chi2_contingency(ct)
        ra = a[metric].mean() * 100
        rb = b[metric].mean() * 100
        lift = (rb - ra) / ra * 100 if ra else 0
        records.append({'Campaign':cname,'Metric':label,
                        'Rate_A':round(ra,3),'Rate_B':round(rb,3),
                        'Lift_%':round(lift,1),'p_value':round(p,4),
                        'Sig':'YES' if p<0.05 else 'NO'})

ab_df  = pd.DataFrame(records)
conv_ab = ab_df[ab_df.Metric=='Conv Rate'].copy().reset_index(drop=True)
print(conv_ab[['Campaign','Rate_A','Rate_B','Lift_%','p_value','Sig']].to_string(index=False))

x, w = np.arange(len(conv_ab)), 0.35
fig, ax = plt.subplots(figsize=(13, 5))
ax.bar(x-w/2, conv_ab['Rate_A'], w, label='Variant A', color='steelblue',  alpha=0.85)
ax.bar(x+w/2, conv_ab['Rate_B'], w, label='Variant B', color='darkorange', alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(conv_ab.Campaign, rotation=12, ha='right')
ax.set_ylabel('Conversion Rate (%)'); ax.set_title('A/B Test — Conversion Rate by Campaign', fontweight='bold')
ax.legend()
for i, row in conv_ab.iterrows():
    top = max(row['Rate_A'], row['Rate_B']) + 0.003
    col = 'green' if row.Sig == 'YES' else 'grey'
    ax.annotate(f"p={row.p_value}\n{row.Sig}", xy=(i, top), ha='center', fontsize=8, color=col)
save('05_ab_testing.png')

# ── 6. CONVERSION FUNNEL ──────────────────────────────────────────────────
section('6 · CONVERSION FUNNEL')
STAGES = ['Sent','Opened','Clicked','Responded','Converted']
COUNTS = [len(df), int(df.opened.sum()), int(df.clicked.sum()),
          int(df.responded.sum()), int(df.converted.sum())]
CUM    = [c/COUNTS[0]*100 for c in COUNTS]
DROP   = [0.0] + [(COUNTS[i-1]-COUNTS[i])/COUNTS[i-1]*100 for i in range(1,len(COUNTS))]

funnel_df = pd.DataFrame({'Stage':STAGES,'Count':COUNTS,
                           'Cumulative_%':[round(v,2) for v in CUM],
                           'Drop-off_%':[round(v,2) for v in DROP]})
print(funnel_df.to_string(index=False))

F_COLORS = ['#2196F3','#4CAF50','#FF9800','#9C27B0','#F44336']
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(STAGES[::-1], COUNTS[::-1], color=F_COLORS, edgecolor='white', linewidth=1.5)
for bar, cnt, pct in zip(bars, COUNTS[::-1], CUM[::-1]):
    ax.text(bar.get_width() + COUNTS[0]*0.01, bar.get_y()+bar.get_height()/2,
            f'{cnt:,}  ({pct:.2f}%)', va='center', fontsize=9, fontweight='bold')
ax.set_xlim(0, COUNTS[0]*1.28)
ax.set_xlabel('Customers')
ax.set_title('Conversion Funnel — Overall', fontweight='bold', fontsize=13)
save('06_funnel_overall.png')

seg_funnel = {}
for s in df.segment.unique():
    sub = df[df.segment==s]
    seg_funnel[s] = [len(sub), int(sub.opened.sum()), int(sub.clicked.sum()),
                     int(sub.responded.sum()), int(sub.converted.sum())]
pct_df = pd.DataFrame(seg_funnel, index=STAGES).div(
         pd.DataFrame(seg_funnel, index=STAGES).iloc[0]) * 100
fig, ax = plt.subplots(figsize=(13,5))
pct_df.T.plot(kind='bar', ax=ax, colormap='Set1', width=0.75)
ax.set_ylabel('% of Sent'); ax.set_xlabel('Segment')
ax.set_title('Funnel Efficiency by Stage & Segment', fontweight='bold')
ax.legend(title='Stage', bbox_to_anchor=(1.02,1), loc='upper left')
ax.tick_params(axis='x', rotation=15)
save('06b_funnel_by_segment.png')

# ── 7. CLV & RFM ──────────────────────────────────────────────────────────
section('7 · CLV & RFM SEGMENTATION')
cust = (df.groupby('customer_id')
          .agg(segment=('segment','first'),
               tenure=('tenure_months','first'),
               total_rev=('revenue','sum'))
          .reset_index())
cust['monthly_val'] = cust['total_rev'] / cust['tenure'].clip(lower=1)
cust['clv']         = (cust['monthly_val'] * cust['tenure']).round(2)
clv_sum = (cust.groupby('segment')['clv']
               .agg(mean='mean',median='median',max='max')
               .round(2).sort_values('mean', ascending=False))
print('  CLV by segment:\n', clv_sum.to_string())

ref_date = df['sent_date'].max()
rfm = (df.groupby('customer_id')
          .agg(recency=('sent_date', lambda x: (ref_date-x.max()).days),
               frequency=('campaign','count'),
               monetary=('revenue','sum'))
          .reset_index())

rfm['R'] = safe_qcut(rfm.recency,                        5, [5,4,3,2,1])
rfm['F'] = safe_qcut(rfm.frequency.rank(method='first'), 5, [1,2,3,4,5])
rfm['M'] = safe_qcut(rfm.monetary.clip(lower=0)+0.01,   5, [1,2,3,4,5])
rfm['RFM'] = rfm.R + rfm.F + rfm.M

def tier(s):
    if s>=13: return 'Champions'
    if s>=11: return 'Loyal'
    if s>= 9: return 'Potential'
    if s>= 7: return 'At Risk'
    return 'Need Attention'

rfm['tier'] = rfm.RFM.apply(tier)
print('\n  RFM tier distribution:\n', rfm.tier.value_counts().to_string())

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('CLV & RFM Customer Intelligence', fontsize=14, fontweight='bold')
clv_plot = cust.groupby('segment')['clv'].mean().sort_values(ascending=False)
axes[0].bar(clv_plot.index, clv_plot.values,
            color=sns.color_palette('viridis', len(clv_plot)))
axes[0].set_title('Average CLV by Segment', fontweight='bold')
axes[0].set_ylabel('CLV (INR)')
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f'{v:,.0f}'))
axes[0].tick_params(axis='x', rotation=15)
tier_c = rfm.tier.value_counts()
axes[1].pie(tier_c.values, labels=tier_c.index, autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette('Set3', len(tier_c)))
axes[1].set_title('RFM Tier Distribution', fontweight='bold')
save('07_clv_rfm.png')

# ── 8. COHORT ANALYSIS ────────────────────────────────────────────────────
section('8 · COHORT ANALYSIS')
df['cohort_year'] = (df['sent_date'].dt.year
                     - (df['tenure_months']/12).astype(int)).clip(upper=2025)
cohort = (df[df.cohort_year>=2015]
            .groupby('cohort_year')
            .agg(customers=('customer_id','nunique'),
                 conversions=('converted','sum'),
                 revenue=('revenue','sum'))
            .reset_index())
cohort['conv_rate']    = (cohort.conversions / cohort.customers * 100).round(3)
cohort['rev_per_cust'] = (cohort.revenue     / cohort.customers).round(2)
print(cohort.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()
ax1.bar(cohort.cohort_year, cohort.customers, color='steelblue', alpha=0.55, width=0.6)
ax2.plot(cohort.cohort_year, cohort.conv_rate, 'o-', color='darkorange', lw=2.5)
ax1.set_xlabel('Account Opening Year (Cohort)')
ax1.set_ylabel('Customer Count', color='steelblue')
ax2.set_ylabel('Conversion Rate (%)', color='darkorange')
ax1.set_title('Cohort Analysis — Customers & Conversion', fontweight='bold')
save('08_cohort_analysis.png')

# ── 9. EXECUTIVE KPI CARD ─────────────────────────────────────────────────
section('9 · EXECUTIVE SUMMARY')
total_rev  = df.revenue.sum()
total_cost = df.campaign_cost.sum()
total_conv = int(df.converted.sum())
roi_all    = (total_rev - total_cost) / total_cost * 100

print(f'  Total Revenue     : INR {total_rev:>12,.0f}')
print(f'  Total Cost        : INR {total_cost:>12,.0f}')
print(f'  Net Profit        : INR {total_rev-total_cost:>12,.0f}')
print(f'  Overall ROI       :     {roi_all:>10.1f}%')
print(f'  Total Conversions :     {total_conv:>10,}')
print(f'  Conversion Rate   :     {total_conv/len(df)*100:>10.3f}%')

TILES = [
    ('Total Revenue',     f'INR {total_rev/1000:.1f}K', '#1976D2'),
    ('Overall ROI',       f'{roi_all:.1f}%',            '#388E3C'),
    ('Conversion Rate',   f'{total_conv/len(df)*100:.3f}%', '#F57C00'),
    ('Total Conversions', f'{total_conv:,}',             '#7B1FA2'),
]
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, (lbl, val, col) in zip(axes, TILES):
    ax.set_facecolor(col + '22')
    ax.text(0.5, 0.60, val, ha='center', va='center', fontsize=26,
            fontweight='bold', color=col, transform=ax.transAxes)
    ax.text(0.5, 0.25, lbl, ha='center', va='center', fontsize=11,
            color='#555', transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle('Executive KPI Dashboard', fontsize=15, fontweight='bold', y=1.02)
save('01_executive_summary.png')

# ── DONE ──────────────────────────────────────────────────────────────────
print('\n' + '='*68)
print('  Pipeline complete.  9 charts -> dashboards/screenshots/')
print('='*68)
