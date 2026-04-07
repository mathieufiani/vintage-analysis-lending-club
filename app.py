import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Portfolio Risk Dashboard", layout="wide")

@st.cache_data
def load_data():
    vintage_curves = pd.read_csv('data/processed/vintage_curves.csv', index_col=0)
    psi_df = pd.read_csv('data/processed/psi_results.csv')
    vintage_by_grade = pd.read_csv('data/processed/vintage_by_grade.csv')
    return vintage_curves, psi_df, vintage_by_grade

vintage_curves, psi_df, vintage_by_grade = load_data()

# --- Risk Score par vintage ---
def compute_risk_score(vintage_curves, psi_df):
    # Normalise dr_24m entre 0 et 1
    dr = vintage_curves['dr_24m'].reset_index()
    dr.columns = ['vintage', 'dr_24m']
    dr['dr_norm'] = (dr['dr_24m'] - dr['dr_24m'].min()) / (dr['dr_24m'].max() - dr['dr_24m'].min())

    # PSI moyen par année
    psi_avg = psi_df.groupby('year')['psi'].mean().reset_index()
    psi_avg.columns = ['year', 'psi_avg']
    psi_avg['psi_norm'] = (psi_avg['psi_avg'] - psi_avg['psi_avg'].min()) / (psi_avg['psi_avg'].max() - psi_avg['psi_avg'].min())

    # Extraire l'année du vintage pour joindre avec PSI
    dr['year'] = dr['vintage'].str[:4].astype(int)
    dr = dr.merge(psi_avg[['year', 'psi_norm']], on='year', how='left').fillna(0)

    # Score combiné : 70% default rate, 30% PSI
    dr['risk_score'] = (0.7 * dr['dr_norm'] + 0.3 * dr['psi_norm']) * 100

    def status(score):
        if score < 33:
            return '🟢 Stable'
        elif score < 66:
            return '🟡 Watch'
        else:
            return '🔴 Alert'

    dr['status'] = dr['risk_score'].apply(status)
    return dr

risk_df = compute_risk_score(vintage_curves, psi_df)

# --- Header ---
st.title("Portfolio Risk Analytics Dashboard")
st.markdown("Lending Club 2007–2018 — Vintage Analysis & Model Drift")

# --- Section 0 : Risk Score ---
st.header("0. Vintage Risk Score")
st.markdown("Composite score: 70% default rate (24m) + 30% average PSI. Thresholds: 🟢 Stable < 33 / 🟡 Watch < 66 / 🔴 Alert ≥ 66")

color_map = {'🟢 Stable': 'green', '🟡 Watch': 'orange', '🔴 Alert': 'red'}

fig_risk = go.Figure()

fig_risk.add_trace(go.Scatter(
    x=risk_df['vintage'],
    y=risk_df['risk_score'],
    mode='lines',
    line=dict(color='lightgray', width=1),
    showlegend=False
))

for status_label, color in color_map.items():
    group = risk_df[risk_df['status'] == status_label]
    fig_risk.add_trace(go.Scatter(
        x=group['vintage'],
        y=group['risk_score'],
        mode='markers',
        name=status_label,
        marker=dict(color=color, size=8)
    ))

fig_risk.add_hline(y=33, line_dash='dash', line_color='orange', annotation_text='Watch threshold')
fig_risk.add_hline(y=66, line_dash='dash', line_color='red', annotation_text='Alert threshold')
fig_risk.update_layout(xaxis_title='Vintage', yaxis_title='Risk Score (0-100)', height=400)
st.plotly_chart(fig_risk, use_container_width=True)

# --- Section 1 : Vintage Curves ---
st.header("1. Vintage Default Curves")

horizon = st.selectbox("Horizon", ['dr_12m', 'dr_24m', 'dr_36m'], index=1)

df_plot = vintage_curves[[horizon]].reset_index()
df_plot.columns = ['vintage', 'default_rate']

fig1 = px.line(df_plot, x='vintage', y='default_rate', markers=True,
               title=f'Cumulative Default Rate — {horizon}',
               labels={'default_rate': 'Default Rate', 'vintage': 'Vintage (Quarter)'})
fig1.update_traces(line_color='steelblue')
fig1.update_layout(height=400)
st.plotly_chart(fig1, use_container_width=True)

# --- Section 2 : PSI ---
st.header("2. Feature Drift — PSI Evolution")

fig2 = px.line(psi_df, x='year', y='psi', color='feature', markers=True,
               title='PSI by Feature — 2015 to 2018',
               labels={'psi': 'PSI', 'year': 'Year'})
fig2.add_hline(y=0.1, line_dash='dash', line_color='orange', annotation_text='Warning (0.1)')
fig2.add_hline(y=0.25, line_dash='dash', line_color='red', annotation_text='Alert (0.25)')
fig2.update_layout(height=400)
st.plotly_chart(fig2, use_container_width=True)

# --- Section 3 : Default by Grade ---
st.header("3. Default Rate by Grade & Vintage")

grade_selected = st.multiselect(
    "Select Grades",
    options=sorted(vintage_by_grade['grade'].unique()),
    default=['A', 'C', 'E', 'G']
)
horizon_grade = st.selectbox("Horizon", ['dr_12m', 'dr_24m', 'dr_36m'], index=1, key='grade_horizon')

df_grade = vintage_by_grade[vintage_by_grade['grade'].isin(grade_selected)].copy()
df_grade['vintage'] = df_grade['vintage'].astype(str)

fig3 = px.line(df_grade, x='vintage', y=horizon_grade, color='grade', markers=True,
               title=f'Default Rate by Grade — {horizon_grade}',
               labels={horizon_grade: 'Default Rate', 'vintage': 'Vintage'})
fig3.update_layout(height=400)
st.plotly_chart(fig3, use_container_width=True)

# --- Section 4 : Vintage Comparison ---
st.header("4. Vintage Comparison — Default vs Prepayment")

vintages_available = sorted(vintage_by_grade['vintage'].astype(str).unique())
vintages_selected = st.multiselect(
    "Select Vintages to Compare",
    options=vintages_available,
    default=['2010Q1', '2013Q1', '2016Q1', '2018Q1']
)

df_comp = vintage_by_grade[vintage_by_grade['vintage'].astype(str).isin(vintages_selected)].copy()
df_comp['vintage'] = df_comp['vintage'].astype(str)

col1, col2 = st.columns(2)

with col1:
    fig4a = px.line(df_comp, x='grade', y='dr_24m', color='vintage', markers=True,
                    title='24m Default Rate by Grade',
                    labels={'dr_24m': 'Default Rate', 'grade': 'Grade'})
    st.plotly_chart(fig4a, use_container_width=True)

with col2:
    fig4b = px.line(df_comp, x='grade', y='prepayment_rate', color='vintage', markers=True,
                    title='Prepayment Rate by Grade',
                    labels={'prepayment_rate': 'Prepayment Rate', 'grade': 'Grade'})
    st.plotly_chart(fig4b, use_container_width=True)