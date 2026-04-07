import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Portfolio Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    vintage_curves = pd.read_csv('data/processed/vintage_curves.csv', index_col=0)
    psi_df = pd.read_csv('data/processed/psi_results.csv')
    vintage_by_grade = pd.read_csv('data/processed/vintage_by_grade.csv')
    return vintage_curves, psi_df, vintage_by_grade

vintage_curves, psi_df, vintage_by_grade = load_data()

st.title("Portfolio Risk Analytics Dashboard")
st.markdown("Lending Club 2007–2018 — Vintage Analysis & Model Drift")


st.header("1. Vintage Default Curves")

horizon = st.selectbox("Horizon", ['dr_12m', 'dr_24m', 'dr_36m'], index=1)

fig, ax = plt.subplots(figsize=(14, 5))
vintage_curves[horizon].plot(ax=ax, marker='o', color='steelblue')
ax.set_title(f'Cumulative Default Rate — {horizon}')
ax.set_ylabel('Default Rate')
ax.set_xlabel('Vintage (Quarter)')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig)


st.header("2. Feature Drift — PSI Evolution")

fig, ax = plt.subplots(figsize=(10, 5))
for feature in psi_df['feature'].unique():
    data = psi_df[psi_df['feature'] == feature]
    ax.plot(data['year'], data['psi'], marker='o', label=feature)

ax.axhline(y=0.1, color='orange', linestyle='--', label='Warning (0.1)')
ax.axhline(y=0.25, color='red', linestyle='--', label='Alert (0.25)')
ax.set_title('PSI by Feature — 2015 to 2018')
ax.set_ylabel('PSI')
ax.set_xlabel('Year')
ax.legend()
plt.tight_layout()
st.pyplot(fig)

st.header("3. Default Rate by Grade & Vintage")

grade_selected = st.multiselect(
    "Select Grades",
    options=sorted(vintage_by_grade['grade'].unique()),
    default=['A', 'C', 'E', 'G']
)

horizon_grade = st.selectbox("Horizon ", ['dr_12m', 'dr_24m', 'dr_36m'], index=1, key='grade_horizon')

fig, ax = plt.subplots(figsize=(14, 5))
for grade in grade_selected:
    data = vintage_by_grade[vintage_by_grade['grade'] == grade]
    ax.plot(data['vintage'].astype(str), data[horizon_grade], marker='o', label=f'Grade {grade}')

ax.set_title(f'Default Rate by Grade — {horizon_grade}')
ax.set_ylabel('Default Rate')
ax.set_xlabel('Vintage')
ax.legend()
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
st.pyplot(fig)

st.header("4. Vintage Comparison — Default vs Prepayment")

vintages_available = sorted(vintage_by_grade['vintage'].astype(str).unique())
vintages_selected = st.multiselect(
    "Select Vintages to Compare",
    options=vintages_available,
    default=['2010Q1', '2013Q1', '2016Q1', '2018Q1']
)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

for vintage in vintages_selected:
    data = vintage_by_grade[vintage_by_grade['vintage'].astype(str) == vintage]
    ax1.plot(data['grade'], data['dr_24m'], marker='o', label=vintage)
    ax2.plot(data['grade'], data['prepayment_rate'], marker='o', label=vintage)

ax1.set_title('24m Default Rate by Grade')
ax1.set_ylabel('Default Rate')
ax1.set_xlabel('Grade')
ax1.legend()

ax2.set_title('Prepayment Rate by Grade')
ax2.set_ylabel('Prepayment Rate')
ax2.set_xlabel('Grade')
ax2.legend()

plt.tight_layout()
st.pyplot(fig)