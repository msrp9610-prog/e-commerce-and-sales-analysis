# CSE4005 — E-Commerce Sales and Customer Analysis Using Data Mining

## What is included
- `data/ecommerce_sales_200.csv`: 200-row, 9-column **synthetic teaching dataset**.
- `src/analyze_and_train.py`: data cleaning, analysis, two ML models, saved evaluation results and charts.
- `src/dashboard.py`: Streamlit dashboard using the CSV and generated model results.
- `src/oracle_etl.py`: optional ETL loader for an Oracle database.
- `sql/oracle_star_schema.sql`: Oracle star-schema DDL.
- `sql/olap_queries.sql`: sample OLAP queries (roll-up, drill-down, slice/dice).
- `reports/project_report_template.md`: report template to complete with your own run results.
- `requirements.txt`: Python dependencies.

**Important:** The included data is synthetic, not real customer/business data. State this in your report and demo. Replace it with an approved real dataset only if your instructor requires real data.

## Recommended setup on macOS
Use Python 3.11 or 3.12 if available. In Terminal:

```bash
cd CSE4005_Ecommerce_Data_Mining_Project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python src/analyze_and_train.py
streamlit run src/dashboard.py
```

The analysis script creates files under `outputs/` including cleaned CSV, model metrics, predictions, and charts. Run it once before launching the dashboard.

## Oracle requirement
The assignment explicitly requires Oracle. The dashboard and ML analysis work without Oracle, but the Oracle warehouse requirement is only complete after you execute `sql/oracle_star_schema.sql` in an Oracle environment and run the ETL loader.

Options:
1. Use your college's Oracle lab/database, if available.
2. Use Oracle Database Free locally if your Mac/CPU/OS setup is supported, or a suitable remote Oracle instance.
3. Use Oracle Live SQL to practice DDL and queries; it may not provide the same direct connection route needed by the Python ETL loader.

Install the optional Python driver:
```bash
pip install oracledb
```
Set connection details as environment variables (do not put passwords in source files):
```bash
export ORACLE_USER="your_username"
export ORACLE_PASSWORD="your_password"
export ORACLE_DSN="host:port/service_name"
```
Then execute the schema in your Oracle SQL client and run:
```bash
python src/oracle_etl.py
```
The ETL script expects the dimension and fact tables in `sql/oracle_star_schema.sql`. It uses bind variables and commits at the end.

## Machine-learning design
Two regression algorithms are implemented:
1. Linear Regression
2. Decision Tree Regressor

Target: `sales_amount`. Predictors include units, unit price, discount, region, category, customer segment, month and weekend flag. A train/test split is used. Metrics include MAE, RMSE and R². Results are educational estimates from a small synthetic dataset, not a business-grade forecast.

## OLAP concepts
- Roll-up: summarize sales from order/date detail to month or year.
- Drill-down: move from year/month totals to individual dates.
- Slice: filter one dimension, e.g. a single region.
- Dice: filter multiple dimensions, e.g. region + category.
- Pivot: rotate dimensions to compare sales by category and region.

## Submission honesty
Run the project yourself, inspect the outputs, add screenshots from your own execution, and fill the report template with actual metric values. Do not claim the Oracle ETL has run unless you actually connect to Oracle and load the rows.
