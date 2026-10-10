from pathlib import Path
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "cleaned_sales.csv"
OUT = ROOT / "outputs"

st.set_page_config(page_title="E-Commerce Sales Analytics", page_icon="📊", layout="wide")
st.title("E-Commerce Sales & Customer Analysis")
st.caption("CSE4005 • Data Warehousing and Data Mining • Synthetic teaching dataset")

if not DATA.exists():
    st.warning("Run the analysis first: python src/analyze_and_train.py")
    st.stop()

df = pd.read_csv(DATA, parse_dates=["order_date"])
with open(OUT/"summary.json", encoding="utf-8") as f:
    summary = json.load(f)

st.sidebar.header("Filters")
regions = sorted(df["region"].dropna().unique())
categories = sorted(df["category"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
filtered = df[df["region"].isin(selected_regions) & df["category"].isin(selected_categories)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total sales", f"₹{filtered['sales_amount'].sum():,.2f}")
c2.metric("Orders", f"{filtered['order_id'].nunique():,}")
c3.metric("Units sold", f"{filtered['units_sold'].sum():,}")
c4.metric("Average order value", f"₹{filtered['sales_amount'].mean():,.2f}" if len(filtered) else "₹0.00")

if filtered.empty:
    st.info("No records match the selected filters.")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Monthly sales (roll-up)")
    monthly = filtered.assign(month=filtered["order_date"].dt.to_period("M").astype(str)).groupby(
        "month", as_index=False)["sales_amount"].sum()
    st.line_chart(monthly.set_index("month"))
with right:
    st.subheader("Sales by category")
    category_sales = filtered.groupby("category")["sales_amount"].sum().sort_values(ascending=False)
    st.bar_chart(category_sales)

left2, right2 = st.columns(2)
with left2:
    st.subheader("Sales by region")
    st.bar_chart(filtered.groupby("region")["sales_amount"].sum().sort_values(ascending=False))
with right2:
    st.subheader("Category × Region (pivot)")
    pivot = filtered.pivot_table(index="category", columns="region", values="sales_amount",
                                 aggfunc="sum", fill_value=0)
    st.dataframe(pivot.style.format("₹{:,.2f}"), use_container_width=True)

st.subheader("Machine-learning model comparison")
metrics_file = OUT / "model_metrics.csv"
if metrics_file.exists():
    metrics = pd.read_csv(metrics_file)
    st.dataframe(metrics, use_container_width=True)
    st.caption("Lower MAE/RMSE is better; R² closer to 1 generally indicates better fit. Results depend on the small synthetic dataset.")
else:
    st.info("Run the analysis script to generate model metrics.")

st.subheader("Filtered records")
st.dataframe(filtered.sort_values("order_date", ascending=False), use_container_width=True)
st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_ecommerce_sales.csv", mime="text/csv")
