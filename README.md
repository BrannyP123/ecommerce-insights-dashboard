# E-commerce Sales & Customer Insights Dashboard

An interactive dashboard analyzing ~540K transactions from a UK-based online
retailer (Dec 2010 – Dec 2011). Built to demonstrate data cleaning,
exploratory analysis, RFM-style customer segmentation, and AI-generated
narrative insights on top of raw transactional data.

## Features
- **Overview metrics**: revenue, orders, average order value, unique customers
- **Revenue trends**: monthly revenue and order volume over time
- **Product performance**: top products by revenue and by units sold
- **Customer insights**: repeat vs. one-time customer breakdown, top customers
  by spend (RFM: Recency, Frequency, Monetary)
- **AI insight summary**: generates a plain-English summary and recommendation
  from the current filtered metrics using Claude

All views respond to sidebar filters (country, date range).

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Clean the raw data (only needs to be run once)
python clean_data.py

# 3. Run the app
streamlit run app.py
```

The app expects `online_retail.csv` in the project folder — the raw dataset
used here is the classic "Online Retail" dataset (also on Kaggle/UCI).

### Enabling the AI insight feature
Set your Anthropic API key as an environment variable before running:
```bash
export ANTHROPIC_API_KEY=your_key_here
```
If no key is set, the app falls back to a rule-based summary so the rest of
the dashboard still works.

## Deploying it live (recommended for your resume/portfolio link)
1. Push this folder to a public GitHub repo (include `clean_retail.csv` so
   the app doesn't depend on the raw file).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with
   GitHub, and deploy the repo — point it at `app.py`.
3. Add your `ANTHROPIC_API_KEY` under the app's "Secrets" settings if you
   want the AI summary feature live.
4. You'll get a public URL you can link directly on your resume/LinkedIn.

## Data notes
- Rows with missing Customer IDs (~25%) were dropped, since they can't be
  attributed to a customer for the segmentation analysis.
- Cancelled orders (invoice numbers starting with "C") are excluded from
  revenue calculations but retained in the dataset with a flag.
- Rows with non-positive prices, or non-positive quantities that aren't
  cancellations, were treated as data entry errors and dropped.

## Possible extensions
- Cohort retention analysis (do customers from a given month's first
  purchase come back in later months?)
- Simple sales forecasting (e.g., a basic time-series model)
- Category-level analysis if you map StockCodes to product categories
