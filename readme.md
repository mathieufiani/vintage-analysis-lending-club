# Vintage Analysis & Model Drift Dashboard
**Lending Club Personal Loans — 2007 to 2018**

## Overview
This project reproduces the core work of a Portfolio Risk Analytics team — monitoring loan portfolio performance over time and detecting when a credit model starts drifting. It is built on 1.35M completed loans from the Lending Club dataset and deployed as an interactive Streamlit dashboard.

## Key Questions & Findings

**Why is the default rate higher after 3 years for 2018 vintages?**
Lending Club started accepting borrowers with lower credit scores post-2015. These subprime borrowers take longer to default, which explains why the gap between 12m and 36m default rates widens significantly for recent vintages.

**Why is the default rate lower in 2013?**
Post-2008, lenders tightened their credit box significantly. By 2013 the portfolio had stabilized — representing the lowest-risk underwriting period in the dataset.

**Is the spike in default rates driven by underwriting or macro factors?**
Primarily underwriting. PSI analysis shows the FICO score distribution shifted significantly in 2018 (PSI = 0.192, approaching the 0.25 alert threshold). Grade-level analysis confirms the deterioration is concentrated in grades E-G while grade A remained stable — a macro shock would have affected all grades proportionally.

## Methodology

**Fixed-horizon vintage curves** — rather than filtering immature vintages, we compute default rates at fixed time horizons (12, 24, 36 months). This allows comparison across all vintages on a consistent basis, including recent ones.

**PSI drift detection** — we used 2013-2014 as the reference period (stable post-crisis underwriting, low default rates) and computed PSI annually from 2015 to 2018 on three features: FICO score, DTI, and annual income.

**Right-censoring** — loans with unknown outcomes (Current, Late, In Grace Period) were excluded from default rate calculations to avoid downward bias.

**Outlier capping** — annual income and DTI were capped at the 90th percentile to remove data errors before PSI bucketing.

## Limitations
- No explicit charge-off date in the dataset — `last_pymnt_d` was used as a proxy, which understates time-to-default by approximately 3-6 months
- Prepayment rate is overstated (~60%) because the dataset ends in 2019, causing loans still active at cutoff to appear as prepaid
- Delinquency rate tracking was not possible due to absence of delinquency date columns

## Dashboard
Live dashboard: [[URL]](https://vintage-analysis-lending-club.streamlit.app/)

## Future Evolution
- Rebuild dashboard in React + D3.js for production-grade interactivity
- Connect vintage analysis to a custom RAG for natural language portfolio querying
- Extend PSI analysis back to 2010 and allow user-defined reference period and thresholds
- Add roll rate analysis (30→60→90 days) as early warning indicators
- Connect to a custom RAG for natural language portfolio querying
- Replace static CSVs with a live PostgreSQL database for real-time monitoring

Note: The Vintage Risk Score is a composite indicator built for monitoring purposes (70% 24m default rate + 30% average PSI). It is not an industry-standard metric but serves as a single-view signal to prioritize vintages requiring closer review.
