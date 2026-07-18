"""
E-commerce Sales & Customer Insights Dashboard

Run locally with: streamlit run app.py
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="E-commerce Insights Dashboard", layout="wide")


@st.cache_data
def load_data():
    df = pd.read_csv("clean_retail.csv", parse_dates=["InvoiceDate"])
    return df


df = load_data()
sales = df[~df["IsCancelled"]]  # exclude cancellations from revenue analysis

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
countries = ["All"] + sorted(sales["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Country", countries)

date_min = sales["InvoiceDate"].min().date()
date_max = sales["InvoiceDate"].max().date()
date_range = st.sidebar.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

filtered = sales.copy()
if selected_country != "All":
    filtered = filtered[filtered["Country"] == selected_country]
if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered["InvoiceDate"].dt.date >= start) & (filtered["InvoiceDate"].dt.date <= end)]

st.title("📊 E-commerce Sales & Customer Insights")
st.caption("Analysis of the UK online retailer transaction dataset (Dec 2010 – Dec 2011)")

# ---------- Overview metrics ----------
total_revenue = filtered["TotalPrice"].sum()
total_orders = filtered["InvoiceNo"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0
total_customers = filtered["CustomerID"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"£{total_revenue:,.0f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Avg Order Value", f"£{avg_order_value:,.2f}")
c4.metric("Unique Customers", f"{total_customers:,}")

st.divider()

# ---------- Trends over time ----------
st.subheader("Revenue Trend")
monthly = filtered.groupby(filtered["InvoiceDate"].dt.to_period("M")).agg(
    Revenue=("TotalPrice", "sum"),
    Orders=("InvoiceNo", "nunique"),
).reset_index()
monthly["InvoiceDate"] = monthly["InvoiceDate"].astype(str)

fig_trend = px.line(monthly, x="InvoiceDate", y="Revenue", markers=True, title="Monthly Revenue")
st.plotly_chart(fig_trend, use_container_width=True)

# ---------- Product performance ----------
st.subheader("Product Performance")
col1, col2 = st.columns(2)

top_products_rev = (
    filtered.groupby("Description")["TotalPrice"].sum().sort_values(ascending=False).head(10)
)
with col1:
    fig_top_rev = px.bar(
        top_products_rev.sort_values(),
        orientation="h",
        title="Top 10 Products by Revenue",
        labels={"value": "Revenue (£)", "Description": ""},
    )
    st.plotly_chart(fig_top_rev, use_container_width=True)

top_products_qty = (
    filtered.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)
)
with col2:
    fig_top_qty = px.bar(
        top_products_qty.sort_values(),
        orientation="h",
        title="Top 10 Products by Units Sold",
        labels={"value": "Units Sold", "Description": ""},
    )
    st.plotly_chart(fig_top_qty, use_container_width=True)

st.divider()

# ---------- Customer insights (RFM) ----------
st.subheader("Customer Insights")

snapshot_date = filtered["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm = filtered.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("TotalPrice", "sum"),
).reset_index()

repeat_customers = (rfm["Frequency"] > 1).sum()
one_time_customers = (rfm["Frequency"] == 1).sum()

col1, col2 = st.columns([1, 2])
with col1:
    fig_repeat = px.pie(
        names=["Repeat customers", "One-time customers"],
        values=[repeat_customers, one_time_customers],
        title="Repeat vs. One-Time Customers",
    )
    st.plotly_chart(fig_repeat, use_container_width=True)

with col2:
    top_customers = rfm.sort_values("Monetary", ascending=False).head(10)
    st.write("**Top 10 Customers by Spend**")
    st.dataframe(
        top_customers[["CustomerID", "Frequency", "Monetary", "Recency"]].rename(
            columns={"Monetary": "Total Spend (£)", "Recency": "Days Since Last Order"}
        ),
        use_container_width=True,
        hide_index=True,
    )

st.divider()

# ---------- AI-generated insight summary ----------
st.subheader("💡 AI Insight Summary")

repeat_pct = repeat_customers / (repeat_customers + one_time_customers) * 100 if (repeat_customers + one_time_customers) else 0
top_country = filtered.groupby("Country")["TotalPrice"].sum().idxmax() if not filtered.empty else "N/A"

if st.button("Generate insight summary"):
    with st.spinner("Analyzing..."):
        try:
            from anthropic import Anthropic
            client = Anthropic()  # reads ANTHROPIC_API_KEY from environment

            prompt = f"""You are a data analyst. Based on the following e-commerce metrics, write a short
(3-4 sentence) plain-English summary of what's happening in the business and one concrete
recommendation. Be specific and reference the numbers.

Total revenue: £{total_revenue:,.0f}
Total orders: {total_orders:,}
Average order value: £{avg_order_value:,.2f}
Unique customers: {total_customers:,}
Repeat customer rate: {repeat_pct:.1f}%
Top country by revenue: {top_country}
Top product by revenue: {top_products_rev.index[0] if len(top_products_rev) else "N/A"}
"""
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            st.info(response.content[0].text)
        except Exception as e:
            st.warning(
                "Couldn't reach the AI API (this feature needs an ANTHROPIC_API_KEY set as an "
                "environment variable / Streamlit secret). Showing a rule-based summary instead."
            )
            st.info(
                f"Revenue reached £{total_revenue:,.0f} across {total_orders:,} orders "
                f"({total_customers:,} unique customers). {top_country} was the top market by "
                f"revenue, and \"{top_products_rev.index[0] if len(top_products_rev) else 'N/A'}\" "
                f"was the best-selling product. Only {repeat_pct:.1f}% of customers placed more "
                f"than one order — improving retention (email follow-ups, loyalty incentives) "
                f"is likely the highest-leverage opportunity here."
            )
