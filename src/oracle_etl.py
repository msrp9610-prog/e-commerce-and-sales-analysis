from pathlib import Path
import os
import pandas as pd
import oracledb

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "outputs" / "cleaned_sales.csv"

def main():
    if not CSV.exists():
        raise SystemExit("Run python src/analyze_and_train.py first.")
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN")
    if not all([user, password, dsn]):
        raise SystemExit("Set ORACLE_USER, ORACLE_PASSWORD, and ORACLE_DSN environment variables first.")
    df = pd.read_csv(CSV, parse_dates=["order_date"])
    conn = oracledb.connect(user=user, password=password, dsn=dsn)
    try:
        cur = conn.cursor()
        # Load small dimension tables, ignoring rows already present.
        for category in sorted(df["category"].dropna().unique()):
            cur.execute("""MERGE INTO dim_product d USING (SELECT :v AS category_name FROM dual) s
                           ON (d.category_name=s.category_name)
                           WHEN NOT MATCHED THEN INSERT (category_name) VALUES (s.category_name)""",
                        v=str(category))
        for region in sorted(df["region"].dropna().unique()):
            cur.execute("""MERGE INTO dim_region d USING (SELECT :v AS region_name FROM dual) s
                           ON (d.region_name=s.region_name)
                           WHEN NOT MATCHED THEN INSERT (region_name) VALUES (s.region_name)""",
                        v=str(region))
        for segment in sorted(df["customer_segment"].dropna().unique()):
            cur.execute("""MERGE INTO dim_customer_segment d USING (SELECT :v AS segment_name FROM dual) s
                           ON (d.segment_name=s.segment_name)
                           WHEN NOT MATCHED THEN INSERT (segment_name) VALUES (s.segment_name)""",
                        v=str(segment))
        for dt in sorted(df["order_date"].dropna().unique()):
            date = pd.Timestamp(dt).to_pydatetime()
            key = int(date.strftime("%Y%m%d"))
            cur.execute("""MERGE INTO dim_date d USING (SELECT :k AS date_key FROM dual) s
                           ON (d.date_key=s.date_key)
                           WHEN NOT MATCHED THEN INSERT
                           (date_key, full_date, day_number, month_number, month_name,
                            quarter_number, year_number, weekend_flag)
                           VALUES (:k, :dt, :dayn, :mon, :monname, :qtr, :yr, :wknd)""",
                        k=key, dt=date, dayn=date.day, mon=date.month,
                        monname=date.strftime("%B"), qtr=((date.month-1)//3)+1,
                        yr=date.year, wknd="Y" if date.weekday() >= 5 else "N")
        conn.commit()

        inserted = 0
        for row in df.itertuples(index=False):
            dt = pd.Timestamp(row.order_date).to_pydatetime()
            date_key = int(dt.strftime("%Y%m%d"))
            cur.execute("SELECT product_key FROM dim_product WHERE category_name=:v", v=row.category)
            product_key = cur.fetchone()[0]
            cur.execute("SELECT region_key FROM dim_region WHERE region_name=:v", v=row.region)
            region_key = cur.fetchone()[0]
            cur.execute("SELECT segment_key FROM dim_customer_segment WHERE segment_name=:v", v=row.customer_segment)
            segment_key = cur.fetchone()[0]
            cur.execute("""MERGE INTO fact_sales f USING (SELECT :oid AS order_id FROM dual) s
                           ON (f.order_id=s.order_id)
                           WHEN NOT MATCHED THEN INSERT
                           (order_id, date_key, product_key, region_key, segment_key,
                            units_sold, unit_price, discount_pct, sales_amount)
                           VALUES (:oid, :dk, :pk, :rk, :sk, :units, :price, :disc, :sales)""",
                        oid=str(row.order_id), dk=date_key, pk=product_key, rk=region_key,
                        sk=segment_key, units=int(row.units_sold), price=float(row.unit_price),
                        disc=float(row.discount_pct), sales=float(row.sales_amount))
            inserted += 1
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM fact_sales")
        print(f"ETL completed. Rows processed: {inserted}; total rows now in FACT_SALES: {cur.fetchone()[0]}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
