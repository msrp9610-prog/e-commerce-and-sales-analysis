# Project Record Book / Report Template
## Title
E-Commerce Sales and Customer Analysis Using Data Mining

## 1. Abstract
This project demonstrates data preprocessing, data warehousing, ETL, OLAP, machine learning, and dashboard-based analysis using a small e-commerce sales dataset. The supplied dataset is synthetic and is intended for academic demonstration.

## 2. Objectives
- Clean and transform sales data using Python.
- Design and implement a dimensional star schema in Oracle.
- Load dimension and fact tables through ETL.
- Demonstrate OLAP roll-up, drill-down, slice, dice and pivot.
- Train and compare two regression algorithms.
- Present useful sales summaries in an interactive dashboard.

## 3. Dataset Description
File: `data/ecommerce_sales_200.csv`
- Number of records: 200 before cleaning.
- Number of columns: 9.
- Fields: order_id, order_date, region, category, customer_segment, units_sold, unit_price, discount_pct, sales_amount.
- Data origin: synthetically generated for this academic project; not real customer transactions.

## 4. System Requirements
Record the actual OS, Python version, libraries and Oracle environment used.

## 5. Methodology
1. Load CSV with pandas.
2. Parse dates, standardize text, convert numeric fields, remove duplicates/invalid records.
3. Derive month and weekend fields for analysis/modeling.
4. Create Oracle dimension tables and a central fact table.
5. Load dimensions and facts through the ETL script.
6. execute OLAP queries and interpret the results.
7. Train Linear Regression and Decision Tree Regressor using a train/test split.
8. Evaluate MAE, RMSE and R².
9. Launch Streamlit dashboard and capture screenshots.

## 6. Star Schema
Dimensions: DIM_DATE, DIM_PRODUCT (category), DIM_REGION, DIM_CUSTOMER_SEGMENT.
Fact: FACT_SALES with order, units, price, discount and sales amount measures.

Insert a screenshot of the schema/ER diagram here.

## 7. ETL and OLAP
Describe extraction from CSV, cleaning/transformation, loading dimensions before facts, and results of each OLAP query. Insert screenshots of executed SQL and row counts.

## 8. Machine Learning
Target: `sales_amount`.
Algorithms: Linear Regression and Decision Tree Regressor.
Record the actual MAE, RMSE and R² from `outputs/model_metrics.csv`. Explain that the dataset is small and synthetic, so metrics are only for learning and not production forecasts.

## 9. Data Analysis and Findings
Use actual results from `outputs/summary.json`, `monthly_sales.csv`, `category_sales.csv`, `region_sales.csv` and dashboard screenshots. Do not invent findings; fill in after running.

## 10. Testing
Record successful tests for CSV loading, cleaning, output generation, dashboard filters, Oracle table creation, ETL row count and OLAP query results.

## 11. Conclusion and Future Scope
Summarize what you learned. Possible future work: use a larger real dataset with permission, include customer-level repeat-purchase behavior, schedule ETL, and deploy the dashboard.

## 12. Viva Preparation
Be ready to explain: data warehouse vs database; star schema; fact vs dimension; ETL; normalization; OLAP; roll-up vs drill-down; slice vs dice; why train/test split; MAE/RMSE/R²; overfitting in decision trees; and why the dataset is synthetic.
