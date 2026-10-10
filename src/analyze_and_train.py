from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "ecommerce_sales_200.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

def main():
    df = pd.read_csv(DATA)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    # Cleaning: standardize text, coerce numeric values, remove duplicates/invalid rows.
    for col in ["region", "category", "customer_segment"]:
        df[col] = df[col].astype("string").str.strip().str.title()
    numeric = ["units_sold", "unit_price", "discount_pct", "sales_amount"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "order_date", "region", "category",
                           "customer_segment", "units_sold", "unit_price",
                           "discount_pct", "sales_amount"])
    df = df[(df["units_sold"] > 0) & (df["unit_price"] > 0) &
            (df["sales_amount"] > 0) & df["discount_pct"].between(0, 1)]
    df["month"] = df["order_date"].dt.month
    df["is_weekend"] = (df["order_date"].dt.dayofweek >= 5).astype(int)
    df["sales_amount"] = df["sales_amount"].round(2)
    df.to_csv(OUT / "cleaned_sales.csv", index=False)

    # Basic descriptive analysis and OLAP-like groupings in pandas.
    summary = {
        "row_count_after_cleaning": int(len(df)),
        "total_sales": round(float(df["sales_amount"].sum()), 2),
        "average_order_value": round(float(df["sales_amount"].mean()), 2),
        "total_units": int(df["units_sold"].sum()),
        "unique_categories": int(df["category"].nunique()),
        "unique_regions": int(df["region"].nunique()),
        "date_min": str(df["order_date"].min().date()),
        "date_max": str(df["order_date"].max().date()),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    df.assign(month_label=df["order_date"].dt.to_period("M").astype(str)).groupby(
        "month_label", as_index=False)["sales_amount"].sum().to_csv(OUT/"monthly_sales.csv", index=False)
    df.groupby("category", as_index=False)["sales_amount"].sum().sort_values(
        "sales_amount", ascending=False).to_csv(OUT/"category_sales.csv", index=False)
    df.groupby("region", as_index=False)["sales_amount"].sum().sort_values(
        "sales_amount", ascending=False).to_csv(OUT/"region_sales.csv", index=False)
    df.pivot_table(index="category", columns="region", values="sales_amount",
                   aggfunc="sum", fill_value=0).to_csv(OUT/"category_region_pivot.csv")

    # Charts
    monthly = pd.read_csv(OUT/"monthly_sales.csv")
    plt.figure(figsize=(10, 4.8))
    plt.plot(monthly["month_label"], monthly["sales_amount"], marker="o")
    plt.title("Monthly Sales"); plt.xlabel("Month"); plt.ylabel("Sales amount")
    plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(OUT/"monthly_sales.png", dpi=150); plt.close()

    cat = pd.read_csv(OUT/"category_sales.csv").sort_values("sales_amount")
    plt.figure(figsize=(8, 4.8))
    plt.barh(cat["category"], cat["sales_amount"])
    plt.title("Sales by Category"); plt.xlabel("Sales amount"); plt.tight_layout()
    plt.savefig(OUT/"category_sales.png", dpi=150); plt.close()

    # Two ML algorithms, with preprocessing contained in each pipeline to avoid leakage.
    features = ["units_sold", "unit_price", "discount_pct", "region", "category",
                "customer_segment", "month", "is_weekend"]
    X, y = df[features], df["sales_amount"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42)
    categorical = ["region", "category", "customer_segment"]
    numeric_features = ["units_sold", "unit_price", "discount_pct", "month", "is_weekend"]
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")),
                              ("scaler", StandardScaler())]), numeric_features),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical)
    ])
    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(max_depth=4, random_state=42)
    }
    metrics, prediction_frames = [], []
    for name, model in models.items():
        pipe = Pipeline([("preprocess", preprocessor), ("model", model)])
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        metrics.append({"model": name,
                        "MAE": round(float(mean_absolute_error(y_test, pred)), 2),
                        "RMSE": round(rmse, 2),
                        "R2": round(float(r2_score(y_test, pred)), 4)})
        prediction_frames.append(pd.DataFrame({
            "model": name, "actual_sales": y_test.to_numpy(),
            "predicted_sales": np.round(pred, 2)
        }))
    pd.DataFrame(metrics).to_csv(OUT/"model_metrics.csv", index=False)
    pd.concat(prediction_frames, ignore_index=True).to_csv(OUT/"model_predictions.csv", index=False)
    print("Analysis complete.")
    print(json.dumps(summary, indent=2))
    print("\nModel metrics:")
    print(pd.DataFrame(metrics).to_string(index=False))
    print(f"\nOutputs saved to: {OUT}")

if __name__ == "__main__":
    main()
