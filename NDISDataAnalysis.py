# %%
import pandas as pd

df = pd.read_csv('Utilisation of plan budgets data March 2026 (1).csv')

# %%
df.head()

# %%
df.info()

# %%
df.describe()

# %%
df.describe(include = 'all')

# %%
df.isnull().sum()

# %%
# How many rows total vs null
print(f"Total rows: {len(df)}")
print(f"Null DsbltyGrpNm: {df['DsbltyGrpNm'].isnull().sum()}")

# What do the null rows look like?
df[df['DsbltyGrpNm'].isnull()]

# %%
# 64 rows out of 144,713 is only 0.04% of the data so dropping them has essentially zero impact on the analysis
df = df.dropna(subset=['DsbltyGrpNm'])

# Verify
print(f"Rows remaining: {len(df)}")

# %%
df.isnull().sum()

# %%
# rename for easier variable references
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(' ','_')

# %%
df.columns

# %%
# convert Utlsn string to real numbers
df['utlstn'] = df['utlstn'].str.rstrip('%').astype(float) / 100

# %%
# ============================================================
# SETUP — reusable helper (run once after your cleaning cells)
# ============================================================
import matplotlib.pyplot as plt
 
ALL = 'ALL'  # the aggregate marker used throughout the dataset
 
# isolate(): keep rows where ONE column varies and every other
# filter column is held at "ALL". This is the core pattern for
# this dataset — we never aggregate rows ourselves, we just select
# the pre-computed rows that isolate the variable we care about.
def isolate(vary_col, fix=None, drop_missing=True):
    """
    vary_col : the column we want to compare across (e.g. 'dsbltygrpnm')
    fix      : dict of columns to pin to a specific value instead of ALL,
               e.g. {'statecd': 'WA'} to drill inside WA
    """
    hold = ['statecd', 'srvcdstrctnm', 'dsbltygrpnm', 'agebnd', 'silorsda', 'suppclass']
    hold.remove(vary_col)
    fix = fix or {}
 
    mask = (df[vary_col] != ALL)              # the variable we study must NOT be ALL
    for c in hold:
        if c in fix:
            mask &= (df[c] == fix[c])         # pinned to a specific value
        else:
            mask &= (df[c] == ALL)            # held at the overall total
 
    out = df[mask].copy()
    if drop_missing:  # remove "Missing" placeholder categories from rankings
        out = out[~out[vary_col].astype(str).str.contains('Missing', case=False, na=False)]
    return out[[vary_col, 'utlstn']].sort_values('utlstn').reset_index(drop=True)

# %%
# ============================================================
# Q1 — What is the overall utilisation rate? (everything = ALL)
# ============================================================
overall = df[(df['statecd'] == ALL) & (df['srvcdstrctnm'] == ALL) &
             (df['dsbltygrpnm'] == ALL) & (df['agebnd'] == ALL) &
             (df['silorsda'] == ALL) & (df['suppclass'] == ALL)]
overall_rate = overall['utlstn'].iloc[0]
print(f"Q1 — Overall scheme utilisation rate: {overall_rate:.0%}")

# %%
# ============================================================
# Q2 — What is the range (highest & lowest) across all groups?
# We scan every single-factor breakdown and report the extremes.
# ============================================================
factors = ['dsbltygrpnm', 'statecd', 'agebnd', 'silorsda', 'suppclass']
ranges = []
for f in factors:
    t = isolate(f)
    ranges.append({'factor': f,
                   'lowest_group': t.iloc[0][f],  'lowest': t.iloc[0]['utlstn'],
                   'highest_group': t.iloc[-1][f], 'highest': t.iloc[-1]['utlstn']})
range_table = pd.DataFrame(ranges)
print("\nQ2 — Utilisation range by factor:")
print(range_table.to_string(index=False))
 

# %%
# ============================================================
# Q3 — Which disability groups have the lowest utilisation?
# ============================================================
q3 = isolate('dsbltygrpnm')
print("\nQ3 — Utilisation by disability group (lowest first):")
print(q3.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(9, 6))
colors = ['#c0392b' if v < overall_rate else '#27ae60' for v in q3['utlstn']]
ax.barh(q3['dsbltygrpnm'], q3['utlstn'], color=colors)
ax.axvline(overall_rate, color='black', linestyle='--', linewidth=1,
           label=f'Overall ({overall_rate:.0%})')
ax.set_xlabel('Utilisation rate'); ax.set_title('Q3 — Utilisation by Disability Group')
ax.legend(); plt.tight_layout(); plt.show()
 

# %%
# ============================================================
# Q4 — Which states/territories have the lowest utilisation?
# ============================================================
q4 = isolate('statecd')
print("\nQ4 — Utilisation by state/territory (lowest first):")
print(q4.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#c0392b' if v < overall_rate else '#27ae60' for v in q4['utlstn']]
ax.bar(q4['statecd'], q4['utlstn'], color=colors)
ax.axhline(overall_rate, color='black', linestyle='--', linewidth=1,
           label=f'Overall ({overall_rate:.0%})')
ax.set_ylabel('Utilisation rate'); ax.set_title('Q4 — Utilisation by State/Territory')
ax.legend(); plt.tight_layout(); plt.show()
 

# %%
# ============================================================
# Q5 — Which age bands have the lowest utilisation?
# Age has a natural order, so we re-sort by age (not by value) for the plot.
# ============================================================
q5 = isolate('agebnd')
print("\nQ5 — Utilisation by age band (lowest first):")
print(q5.to_string(index=False))
 
age_order = ['0 to 8', '9 to 14', '15 to 18', '19 to 24', '25 to 34',
             '35 to 44', '45 to 54', '55 to 64', '65+']
q5_ordered = q5.set_index('agebnd').reindex(age_order).reset_index()
 
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(q5_ordered['agebnd'], q5_ordered['utlstn'], marker='o', color='#2c3e50')
ax.axhline(overall_rate, color='black', linestyle='--', linewidth=1,
           label=f'Overall ({overall_rate:.0%})')
ax.set_ylabel('Utilisation rate'); ax.set_xlabel('Age band')
ax.set_title('Q5 — Utilisation by Age Band'); ax.legend()
plt.xticks(rotation=45); plt.tight_layout(); plt.show()
 

# %%
# ============================================================
# Q6 — Does having SIL/SDA support change utilisation?
# ============================================================
q6 = isolate('silorsda', drop_missing=False)
print("\nQ6 — Utilisation by SIL/SDA status:")
print(q6.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(5, 5))
ax.bar(q6['silorsda'], q6['utlstn'], color=['#c0392b', '#27ae60'])
ax.set_ylabel('Utilisation rate')
ax.set_title('Q6 — SIL/SDA vs No SIL/SDA')
for i, v in enumerate(q6['utlstn']):
    ax.text(i, v + 0.01, f'{v:.0%}', ha='center')
plt.tight_layout(); plt.show()

# %%
# ============================================================
# Q7 — Which support class has the lowest utilisation?
# ============================================================
q7 = isolate('suppclass')
print("\nQ7 — Utilisation by support class (lowest first):")
print(q7.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(7, 4))
colors = ['#c0392b' if v < overall_rate else '#27ae60' for v in q7['utlstn']]
ax.bar(q7['suppclass'], q7['utlstn'], color=colors)
ax.axhline(overall_rate, color='black', linestyle='--', linewidth=1,
           label=f'Overall ({overall_rate:.0%})')
ax.set_ylabel('Utilisation rate'); ax.set_title('Q7 — Utilisation by Support Class')
ax.legend(); plt.tight_layout(); plt.show()

# %%
# ============================================================
# Q8 — Is low utilisation in a state driven by specific districts?
# We drill into the LOWEST state from Q4 by pinning statecd and
# letting srvcdstrctnm vary.
# ============================================================
lowest_state = q4.iloc[0]['statecd']
q8 = isolate('srvcdstrctnm', fix={'statecd': lowest_state})
print(f"\nQ8 — Districts within {lowest_state} (lowest first):")
print(q8.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(9, 6))
state_avg = q4.iloc[0]['utlstn']
colors = ['#c0392b' if v < state_avg else '#27ae60' for v in q8['utlstn']]
ax.barh(q8['srvcdstrctnm'], q8['utlstn'], color=colors)
ax.axvline(state_avg, color='black', linestyle='--', linewidth=1,
           label=f'{lowest_state} avg ({state_avg:.0%})')
ax.set_xlabel('Utilisation rate')
ax.set_title(f'Q8 — District Utilisation within {lowest_state}')
ax.legend(); plt.tight_layout(); plt.show()

# %%
# ============================================================
# Q9 — Is low utilisation in a disability group concentrated
# in specific age bands? Drill into the LOWEST disability from Q3.
# ============================================================
lowest_disability = q3.iloc[0]['dsbltygrpnm']
q9 = isolate('agebnd', fix={'dsbltygrpnm': lowest_disability})
q9_ordered = q9.set_index('agebnd').reindex(age_order).reset_index().dropna()
print(f"\nQ9 — {lowest_disability} utilisation by age band:")
print(q9.to_string(index=False))
 
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(q9_ordered['agebnd'], q9_ordered['utlstn'], marker='o', color='#c0392b',
        label=lowest_disability)
ax.axhline(overall_rate, color='black', linestyle='--', linewidth=1,
           label=f'Overall ({overall_rate:.0%})')
ax.set_ylabel('Utilisation rate'); ax.set_xlabel('Age band')
ax.set_title(f'Q9 — {lowest_disability} Utilisation by Age')
ax.legend(); plt.xticks(rotation=45); plt.tight_layout(); plt.show()

# %%
# All districts nationally, everything else held at ALL
nat = df[(df['statecd'] != 'ALL') &        # district belongs to a real state
         (df['srvcdstrctnm'] != 'ALL') &    # vary district
         (df['dsbltygrpnm'] == 'ALL') &
         (df['agebnd'] == 'ALL') &
         (df['silorsda'] == 'ALL') &
         (df['suppclass'] == 'ALL')]
nat = nat[nat['srvcdstrctnm'] != 'Other']  # drop the data-quality bucket
nat = nat[['statecd','srvcdstrctnm','utlstn']].sort_values('utlstn')
print(nat.head(15))   # the 15 worst districts in the country

# %%
lo = pd.read_csv('Longitudinal Outcomes data (1).csv')

# %%
lo.head()

# %%
lo.info()

# %%
lo.describe()

# %%
lo.describe(include = 'all')

# %%
lo.isnull().sum()

# %%
# checking for any "na"
(lo.astype(str).apply(lambda col: col.str.strip().str.lower() == 'na')).sum()

# %%
lo.columns = lo.columns.str.lower()
lo.columns = lo.columns.str.replace(' ', '_')

# %%
lo.columns

# %%
# --- clean ---
re_cols = [f'percentage_reassessment_{i}' for i in range(1, 11)]
for c in ['percentage_baseline'] + re_cols:
    lo[c] = pd.to_numeric(lo[c], errors='coerce')
 
# --- participant-only ---
part = lo[lo['questionnaire'].str.startswith('Participant')].copy()
 
# --- flip 3 reverse-coded questions (higher = worse -> complement) ---
REVERSE = [
    '% unable to do a course or training they wanted to do in the last 12 months',
    '% with concerns in 6 or more of the areas: gross motor skills, fine motor skills, self-care, eating, social interaction, communication, cognitive development, sensory processing',
    '% with no friends other than family or paid staff',
]
fm = part['indicator_description'].isin(REVERSE)
for c in ['percentage_baseline'] + re_cols:
    part.loc[fm, c] = 1 - part.loc[fm, c]
 
part['is_help'] = part['indicator_description'].str.strip().str.lower().str.startswith('has')
 
# --- EXPLICIT theme dictionary (every question hand-assigned) ---
THEME_MAP = {
    # ----- TYPE A: status -----
    # Employment/Education
    '% of children attending school in a mainstream class': 'Employment/Education',
    '% unable to do a course or training they wanted to do in the last 12 months': 'Employment/Education',
    '% who currently attend or previously attended school in a mainstream class': 'Employment/Education',
    '% who have a paid job': 'Employment/Education',
    '% who participate in education, training or skill development': 'Employment/Education',
    # Health/Development
    '% developing functional, learning and coping skills appropriate to their ability and circumstances': 'Health/Development',
    '% who did not have any difficulties accessing health services': 'Health/Development',
    '% who rate their health as good, very good or excellent': 'Health/Development',
    '% with concerns in 6 or more of the areas: gross motor skills, fine motor skills, self-care, eating, social interaction, communication, cognitive development, sensory processing': 'Health/Development',
    # Social/Community
    '% of children who can make friends with people outside the family': 'Social/Community',
    '% of children who participate in age appropriate community, cultural or religious activities': 'Social/Community',
    '% of children who spend time after school and on weekends with friends and/or in mainstream programs': 'Social/Community',
    '% of children who spend time with friends without an adult present': 'Social/Community',
    '% who have been actively involved in a community, cultural or religious group in the last 12 months': 'Social/Community',
    '% who volunteer': 'Social/Community',
    '% with no friends other than family or paid staff': 'Social/Community',
    '% who had been given the opportunity to participate in a self-advocacy group meeting': 'Social/Community',
    # Choice/Control/Independence
    '% of children who have a genuine say in decisions about themselves': 'Choice/Control/Independence',
    '% who are happy with the level of independence/control they have now': 'Choice/Control/Independence',
    '% who are happy with their home': 'Choice/Control/Independence',
    '% who choose what they do each day': 'Choice/Control/Independence',
    '% who choose who supports them': 'Choice/Control/Independence',
    '% who feel safe or very safe in their home': 'Choice/Control/Independence',
    '% who say their child is able to tell them what he/she wants': 'Choice/Control/Independence',
    '% who say their child is becoming more independent': 'Choice/Control/Independence',
    '% who want more choice and control in their life': 'Choice/Control/Independence',
 
    # ----- TYPE B: "Has NDIS helped" -----
    # Employment/Education
    "Has the NDIS improved your child's access to education?": 'Employment/Education',
    "Has your involvement with the NDIS helped you find a job that's right for you?": 'Employment/Education',
    "Has your involvement with the NDIS helped you to learn things you want to learn or to take courses you want to take?": 'Employment/Education',
    # Health/Development
    "Has the NDIS improved your child's access to specialist services?": 'Health/Development',
    "Has the NDIS improved your child's development?": 'Health/Development',
    "Has your involvement with the NDIS improved your health and wellbeing?": 'Health/Development',
    # Social/Community
    'Has the NDIS helped you be more involved?': 'Social/Community',
    'Has the NDIS helped you to meet more people?': 'Social/Community',
    "Has the NDIS improved how your child fits into community life?": 'Social/Community',
    "Has the NDIS improved how your child fits into family life?": 'Social/Community',
    "Has the NDIS improved your child's relationships with family and friends?": 'Social/Community',
    "Has the NDIS improved your child's social and recreational life?": 'Social/Community',
    # Choice/Control/Independence
    'Has the NDIS helped you have more choices and more control over your life?': 'Choice/Control/Independence',
    'Has the NDIS helped you with daily living activities?': 'Choice/Control/Independence',
    'Has the NDIS helped your child to become more independent?': 'Choice/Control/Independence',
    "Has your involvement with the NDIS helped you to choose a home that's right for you?": 'Choice/Control/Independence',
    "Has the NDIS helped increase your child's ability to communicate what they want?": 'Choice/Control/Independence',
}
 
part['theme'] = part['indicator_description'].map(THEME_MAP)
# drop unmapped rows (the 3 conditional "Of those..." sub-questions)
part = part[part['theme'].notna()]
 
# --- each cohort uses its own reassessment ---
def cohort_latest(row):
    n = int(row['number_of_plan_reassessments'])
    return row[f'percentage_reassessment_{n}']
 
# reusable plotter: one theme x cohort line plot for a given age band
def plot_band(data, ageband, value_col, title, ylabel, zero_line=False):
    grid = (data[data['questionnaire'] == ageband]
            .groupby(['theme', 'number_of_plan_reassessments'])[value_col]
            .mean().unstack())
    fig, ax = plt.subplots(figsize=(10, 5))
    for theme_name, row in grid.iterrows():
        ax.plot(row.index, row.values, marker='o', label=theme_name)
    if zero_line:
        ax.axhline(0, color='grey', linestyle='--', linewidth=1)
    ax.set_xlabel('Cohort (years in scheme)'); ax.set_ylabel(ylabel)
    ax.set_title(title); ax.legend(fontsize=8); plt.tight_layout(); plt.show()
    return grid
 

# %%
# ============================================================
# ===== SECTION 1: "NDIS HELPED / IMPROVED" (NA baseline) — 4 PLOTS =====
# Measure = LEVEL (the reassessment % itself; higher = better).
# ============================================================
B = part[part['is_help']].copy()
B['score'] = B.apply(cohort_latest, axis=1)
 
print("="*60)
print("SECTION 1 — NDIS HELPED/IMPROVED (level), 4 plots by age band")
print("="*60)
 
plot_band(B, 'Participant 0 to before school', 'score',
          'NDIS Helped — 0 to before school (level)', 'Help-level')                 # Plot 1
plot_band(B, 'Participant starting school to 14', 'score',
          'NDIS Helped — starting school to 14 (level)', 'Help-level')              # Plot 2
plot_band(B, 'Participant 15 to 24', 'score',
          'NDIS Helped — 15 to 24 (level)', 'Help-level')                           # Plot 3
plot_band(B, 'Participant 25 and over', 'score',
          'NDIS Helped — 25 and over (level)', 'Help-level')                        # Plot 4
 

# %%
# ============================================================
# ===== SECTION 2: GENERAL / STATUS (baseline present) — 4 PLOTS =====
# Measure = CHANGE (Rn - baseline; positive = improved, negative = worse).
# ============================================================
A = part[~part['is_help']].copy()
A['score'] = A.apply(lambda r: cohort_latest(r) - r['percentage_baseline'], axis=1)
 
print("="*60)
print("SECTION 2 — STATUS CHANGE (Rn - baseline), 4 plots by age band")
print("="*60)
 
plot_band(A, 'Participant 0 to before school', 'score',
          'Status Change — 0 to before school (Rn - baseline)', 'Change', zero_line=True)   # Plot 5
plot_band(A, 'Participant starting school to 14', 'score',
          'Status Change — starting school to 14 (Rn - baseline)', 'Change', zero_line=True) # Plot 6
plot_band(A, 'Participant 15 to 24', 'score',
          'Status Change — 15 to 24 (Rn - baseline)', 'Change', zero_line=True)              # Plot 7
plot_band(A, 'Participant 25 and over', 'score',
          'Status Change — 25 and over (Rn - baseline)', 'Change', zero_line=True)           # Plot 8

# %%
# ============================================================
# SUMMARY TABLES — band x theme (collapse cohort into one number)
# Reuses B (Section 1, level) and A (Section 2, change) already built above.
# GROUP A = "NDIS helped" LEVEL ; GROUP B = status CHANGE (Rn - baseline)
# NaN = that age band was not asked any question in that theme.
# ============================================================
short = {'Participant 0 to before school': '0-7',
         'Participant starting school to 14': '7-14',
         'Participant 15 to 24': '15-24',
         'Participant 25 and over': '25+'}
band_order  = ['0-7', '7-14', '15-24', '25+']
theme_order = ['Choice/Control/Independence', 'Employment/Education',
               'Health/Development', 'Social/Community']

# ----- GROUP A: NDIS helped (LEVEL) — reuses B from Section 1 -----
groupA = (B.groupby([B['questionnaire'].map(short), 'theme'])['score']
          .mean().unstack()
          .reindex(index=band_order, columns=theme_order).round(3))
print("GROUP A (NDIS helped — LEVEL): band x theme")
print(groupA.to_string())

# ----- GROUP B: status CHANGE (Rn - baseline) — reuses A from Section 2 -----
groupB = (A.groupby([A['questionnaire'].map(short), 'theme'])['score']
          .mean().unstack()
          .reindex(index=band_order, columns=theme_order).round(3))
print("\nGROUP B (status CHANGE — Rn minus baseline): band x theme")
print(groupB.to_string())

# %%
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

# %%
# ---------- 1. Build the modelling frame: GRANULAR rows only ----------
# Drop every 'ALL' rollup row (these are totals that CONTAIN the breakdowns
# -> including them would double/triple-count the same people).
dims = ['statecd', 'srvcdstrctnm', 'dsbltygrpnm', 'agebnd', 'silorsda', 'suppclass']
m = df[(df[dims] != ALL).all(axis=1)].copy()
# Drop 'Missing' placeholder categories (data-quality buckets, not real groups)
for c in dims:
    m = m[~m[c].astype(str).str.contains('Missing', case=False, na=False)]
print(f"Granular modelling rows: {len(m)}")

# %%
# ---------- 2. Feature engineering ----------
# Collapse 18 disability groups -> 5 clinically sensible buckets
disab_map = {
    'Hearing Impairment': 'Sensory/Speech', 'Visual Impairment': 'Sensory/Speech',
    'Other Sensory/Speech': 'Sensory/Speech',
    'Intellectual Disability': 'Intellectual/Developmental', 'Down Syndrome': 'Intellectual/Developmental',
    'Autism': 'Intellectual/Developmental', 'Developmental delay': 'Intellectual/Developmental',
    'Global developmental delay': 'Intellectual/Developmental',
    'Cerebral Palsy': 'Physical/Neurological', 'Spinal Cord Injury': 'Physical/Neurological',
    'ABI': 'Physical/Neurological', 'Stroke': 'Physical/Neurological',
    'Multiple Sclerosis': 'Physical/Neurological', 'Other Neurological': 'Physical/Neurological',
    'Other Physical': 'Physical/Neurological',
    'Psychosocial disability': 'Psychosocial',
    'Other': 'Other',
}
m['disability_group'] = m['dsbltygrpnm'].map(disab_map)
 
# Collapse 84 districts -> Metro vs Regional/Remote (the real signal)
m['region_type'] = np.where(m['srvcdstrctnm'].str.contains('Metro', case=False, na=False),
                            'Metro', 'Regional/Remote')
 
# Set reference (baseline) categories so coefficients read against a sensible base
m['disability_group'] = pd.Categorical(m['disability_group'],
    categories=['Intellectual/Developmental', 'Physical/Neurological', 'Psychosocial',
                'Sensory/Speech', 'Other'])                          # base = Intellectual/Developmental
m['agebnd'] = pd.Categorical(m['agebnd'],
    categories=['25 to 34', '0 to 8', '9 to 14', '15 to 18', '19 to 24',
                '35 to 44', '45 to 54', '55 to 64', '65+'])          # base = 25 to 34 (prime-age)
m['silorsda']   = pd.Categorical(m['silorsda'],   categories=['No', 'Yes'])         # base = No
m['suppclass']  = pd.Categorical(m['suppclass'],  categories=['Core', 'Capital', 'Capacity Building'])  # base = Core
m['region_type'] = pd.Categorical(m['region_type'], categories=['Metro', 'Regional/Remote'])  # base = Metro
 

# %%
# ---------- 3. Fit fractional logit (Binomial GLM, logit link) ----------
# HC0 = robust standard errors (guards against the proportion variance structure).
model = smf.glm('utlstn ~ disability_group + agebnd + silorsda + suppclass + region_type',
                data=m, family=sm.families.Binomial()).fit(cov_type='HC0')
print("\n" + "="*60)
print("FRACTIONAL LOGIT — raw coefficients (log-odds)")
print("="*60)
print(model.summary())

# %%
# ---------- 4. Marginal effects: convert log-odds -> percentage points ----------
# This is the interpretable output: "factor X changes utilisation by Y pp,
# holding everything else constant." Read THIS to the client, not log-odds.
margeff = model.get_margeff(method='dydx')
print("\n" + "="*60)
print("AVERAGE MARGINAL EFFECTS (percentage-point change in utilisation)")
print("="*60)
print(margeff.summary())

# %%
# ---------- 5. Ranked significant drivers (the Q2 answer) ----------
me = pd.DataFrame({
    'effect_pp': margeff.margeff * 100,          # percentage points
    'std_err_pp': margeff.margeff_se * 100,
    'pvalue': margeff.pvalues,
}, index=model.params.index[1:])                  # drop intercept
me['significant'] = me['pvalue'] < 0.05
me['ci_low_pp']  = me['effect_pp'] - 1.96 * me['std_err_pp']
me['ci_high_pp'] = me['effect_pp'] + 1.96 * me['std_err_pp']
ranked = me[me['significant']].reindex(
    me[me['significant']]['effect_pp'].abs().sort_values(ascending=False).index)
print("\n" + "="*60)
print("RANKED SIGNIFICANT DRIVERS (largest absolute effect first)")
print("="*60)
print(ranked[['effect_pp', 'ci_low_pp', 'ci_high_pp', 'pvalue']].round(2).to_string())

# %%
# ---------- 6. SEVERITY: convert utilisation gap -> $ committed-but-unspent ----------
# Severity = (1 - utilisation) x average plan budget per participant.
# NOTE: set AVG_PLAN_BUDGET to the real figure from the Participant Number &
# Plan Budget dataset; placeholder used here for illustration.
AVG_PLAN_BUDGET = 70000   # <-- replace with actual average annual plan budget ($)
seg = (m.groupby(['disability_group', 'agebnd', 'silorsda', 'suppclass', 'region_type'],
                 observed=True)['utlstn'].mean().reset_index())
seg['unspent_per_participant'] = (1 - seg['utlstn']) * AVG_PLAN_BUDGET
print("\n" + "="*60)
print(f"SEVERITY — $ committed-but-unspent per participant (avg budget ${AVG_PLAN_BUDGET:,})")
print("Top 10 worst segments:")
print("="*60)
print(seg.sort_values('unspent_per_participant', ascending=False)
        .head(10)[['disability_group','agebnd','silorsda','suppclass','region_type',
                   'utlstn','unspent_per_participant']].round(2).to_string(index=False))

# %%
import numpy as np
 
# ---------- Load & clean the budget dataset ----------
pb = pd.read_csv('Participant numbers and plan budgets data March 2026 (2).csv')
pb.columns = pb.columns.str.lower()
# parse the budget ($ string with commas); '<11' counts -> NaN
pb['bdgt']   = pd.to_numeric(pb['avganlsdcmtdsuppbdgt'].astype(str).str.replace(',', ''), errors='coerce')
pb['nptcpt'] = pd.to_numeric(pb['actvprtcpnt'].astype(str).str.replace('<11', '').replace('', np.nan), errors='coerce')
# align support-class spelling to the utilisation data
pb['suppclass'] = pb['suppclass'].replace({'CapacityBuilding': 'Capacity Building'})

# %%
# ---------- Keep budget rows at the 5-key granular level (no ALL/Missing) ----------
KEYS = ['statecd', 'srvcdstrctnm', 'dsbltygrpnm', 'agebnd', 'suppclass']   # NOTE: no silorsda
pbg = pb[(pb[KEYS] != 'ALL').all(axis=1)].copy()
for c in KEYS:
    pbg = pbg[~pbg[c].astype(str).str.contains('Missing', case=False, na=False)]
pbg = pbg[KEYS + ['bdgt', 'nptcpt']]

# %%
# ---------- Join budgets onto the granular utilisation rows ('m' from the GLM) ----------
sev = m.merge(pbg, on=KEYS, how='left')
print(f"Budget match rate onto utilisation rows: {sev['bdgt'].notna().mean():.1%} "
      f"({sev['bdgt'].notna().sum()}/{len(sev)})")
sev = sev.dropna(subset=['bdgt'])   # drop unmatched / privacy-suppressed (~1.8%)

# %%
# ---------- SEVERITY per participant = (1 - utilisation) x real segment budget ----------
sev['unspent_per_participant'] = (1 - sev['utlstn']) * sev['bdgt']
 
# ---------- Display (utilisation shown as a %, NOT blanket-rounded) ----------
out = sev.sort_values('unspent_per_participant', ascending=False).head(10).copy()
out['utilisation'] = (out['utlstn'] * 100).round(0).astype(int).astype(str) + '%'   # e.g. 23%, not 0.0
out['budget'] = out['bdgt'].round(0).astype(int)
out['unspent_per_participant'] = out['unspent_per_participant'].round(0).astype(int)
 
print("\n" + "="*78)
print("SEVERITY (REAL budgets) — $ committed-but-unspent PER PARTICIPANT")
print("Top 10 worst segments  (SIL/SDA not available in budget data)")
print("="*78)
print(out[['disability_group', 'agebnd', 'suppclass', 'region_type',
           'utilisation', 'budget', 'unspent_per_participant']].to_string(index=False))
 
print("\nNOTE: 'utilisation' is the real rate shown as a %; 'unspent' = (1 - rate) x budget.")
print("Largest per-person unspent amounts are LARGE-PLAN segments (older, Core),")
print("NOT the lowest-utilisation-rate segments — dollar priority differs from rate priority.")

# %%
# ---------- expected loss per row (needs participant count) ----------
el = sev.dropna(subset=['nptcpt']).copy()
el['expected_loss'] = (1 - el['utlstn']) * el['bdgt'] * el['nptcpt']
 

# %%
# ============================================================
# 4.1 BASE CASE — total annual committed-but-undelivered funding
# Computed on CORE only (avoids cross-support-class double-counting).
# ============================================================
core = el[el['suppclass'] == 'Core']
base_case = core['expected_loss'].sum()
print("="*70)
print("4.1 BASE CASE — 'do nothing' annual undelivered funding (CORE only)")
print("="*70)
print(f"Total expected annual committed-but-undelivered funding: ${base_case:,.0f}")
print(f"(Core support class only, to avoid double-counting people across classes.)")
print(f"Interpretation: if the current utilisation pattern persists, ~${base_case/1e9:.1f}bn")
print(f"of Core funding is allocated but not converted into support each year.")
 
# Per-support-class (shown SEPARATELY, not summed) for context
print("\nExpected loss BY support class (shown separately — do NOT sum across):")
for sc in ['Core', 'Capital', 'Capacity Building']:
    tot = el[el['suppclass'] == sc]['expected_loss'].sum()
    print(f"   {sc:18s}: ${tot:,.0f}")

# %%
# ============================================================
# 4.2 EXPECTED-LOSS BREAKDOWN — where the (Core) loss comes from
# Same total as 4.1, sliced one dimension at a time (3-9 rows each).
# ============================================================
print("\n" + "="*70)
print("4.2 EXPECTED-LOSS BREAKDOWN (Core) — where the $ is concentrated")
print("="*70)
for dim in ['disability_group', 'agebnd', 'region_type']:
    roll = core.groupby(dim, observed=True)['expected_loss'].sum().sort_values(ascending=False)
    pct = (roll / roll.sum() * 100).round(1)
    tbl = pd.DataFrame({'expected_loss': roll.apply(lambda x: f"${x:,.0f}"),
                        'share_%': pct})
    print(f"\nBy {dim}:")
    print(tbl.to_string())

# %%
 
# ============================================================
# 4.3 TAIL RISK — the extreme, compounding-disadvantage segments
# Where multiple risk factors STACK and utilisation craters.
# Defined as segments in the bottom 5% of utilisation (the left tail).
# ============================================================
tail_cut = el['utlstn'].quantile(0.05)
tail = el[el['utlstn'] <= tail_cut].copy()
print("\n" + "="*70)
print(f"4.3 TAIL RISK — worst 5% of segments by utilisation (rate <= {tail_cut:.0%})")
print("="*70)
print(f"Segments in tail: {len(tail)}  |  participants: {tail['nptcpt'].sum():,.0f}")
print(f"Mean utilisation in tail: {tail['utlstn'].mean():.0%}  (vs {el['utlstn'].mean():.0%} overall)")
print("\nMost common profile of tail segments (compounding disadvantage):")
for dim in ['disability_group', 'agebnd', 'silorsda', 'suppclass', 'region_type']:
    top = tail[dim].value_counts(normalize=True).head(1)
    print(f"   {dim:18s}: {top.index[0]} ({top.iloc[0]:.0%} of tail segments)")
 
print("\nTop 10 tail segments (lowest utilisation, with their loss):")
tail_show = tail.sort_values('utlstn').head(10).copy()
tail_show['utilisation'] = (tail_show['utlstn']*100).round(0).astype(int).astype(str)+'%'
tail_show['expected_loss'] = tail_show['expected_loss'].round(0).astype(int)
print(tail_show[['disability_group','agebnd','silorsda','suppclass','region_type',
                 'utilisation','nptcpt','expected_loss']].to_string(index=False))

# %%
# ============================================================
# 4.4 UNPRICED RISK — known unknowns to flag (not computable here)
# ============================================================
print("\n" + "="*70)
print("4.4 UNPRICED RISK (flagged, not quantified)")
print("="*70)
print("- SIL/SDA not in budget data -> severity excludes a top utilisation driver.")
print("- Disability/region/support-class outcomes NOT in outcomes data -> cannot")
print("  confirm whether under-utilising segments are genuinely underserved.")
print("- Single March-2026 snapshot -> no multi-year/economic-cycle variation priced.")
print("- Budget = per-segment average (rounded $1,000, small cells suppressed).")

# %%



