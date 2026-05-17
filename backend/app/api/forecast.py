from fastapi import APIRouter
import pandas as pd
from pathlib import Path

router = APIRouter()


def load_data():
    csv_path = Path(__file__).resolve().parents[2] / "datasets" / "retail_demand_dataset.csv"

    if not csv_path.exists():
        return None, None, None

    df = pd.read_csv(csv_path)

    num_cols = df.select_dtypes(include="number").columns.tolist()
    if not num_cols:
        return df, None, csv_path

    demand_col = "demand" if "demand" in df.columns else num_cols[0]

    df[demand_col] = pd.to_numeric(df[demand_col], errors="coerce").fillna(0)

    if "price" not in df.columns:
        df["price"] = 100

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(100)
    df["revenue"] = df[demand_col] * df["price"]

    return df, demand_col, csv_path


@router.get("/summary")
def summary():
    df, demand_col, csv_path = load_data()

    if df is None or demand_col is None:
        return {
            "message": "Dataset missing or numeric column missing",
            "total_forecast_units": 0,
            "revenue_forecast": 0,
            "stockout_risk_products": 0,
            "confidence": 0,
            "forecast_data": []
        }

    total_units = int(df[demand_col].sum())
    revenue = int(df["revenue"].sum())

    avg_demand = df[demand_col].mean()
    std_demand = df[demand_col].std()

    stockout_risk_products = int(
        (df[demand_col] > df[demand_col].quantile(0.75)).sum()
    )

    confidence = 0 if avg_demand == 0 else round(
        max(50, min(99, 100 - ((std_demand / avg_demand) * 10))),
        2
    )

    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    forecast_data = [
        {
            "day": f"Day {i + 1}",
            "demand": int(value),
            "month": months[i % 12]
        }
        for i, value in enumerate(df[demand_col].head(120).tolist())
    ]

    return {
        "message": "ok",
        "total_forecast_units": total_units,
        "revenue_forecast": revenue,
        "stockout_risk_products": stockout_risk_products,
        "confidence": confidence,
        "forecast_data": forecast_data
    }


@router.get("/analysis")
def analysis():
    df, demand_col, csv_path = load_data()

    if df is None or demand_col is None:
        return {
            "top_products": [],
            "stock_risk": [],
            "revenue_trend": []
        }

    category_col = None
    for col in ["product_id", "product", "category", "sku", "store", "store_id"]:
        if col in df.columns:
            category_col = col
            break

    if category_col is None:
        text_cols = df.select_dtypes(include="object").columns.tolist()
        if text_cols:
            category_col = text_cols[0]

    if category_col is None:
        df["product_group"] = "Product " + (df.index % 10 + 1).astype(str)
        category_col = "product_group"

    top_products = (
        df.groupby(category_col)[demand_col]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={category_col: "name", demand_col: "demand"})
        .to_dict("records")
    )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_label"] = df["date"].dt.strftime("%d %b")

    revenue_trend = (
        df.groupby("date_label")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"date_label": "name"})
        .head(60)
        .to_dict("records")
    )

    risk_df = (
        df.groupby(category_col)[demand_col]
        .agg(["mean", "sum", "std", "count"])
        .reset_index()
        .fillna(0)
    )

    risk_df["demand_pressure"] = risk_df["sum"] / risk_df["sum"].max()
    risk_df["volatility"] = risk_df["std"] / (risk_df["mean"] + 1)

    risk_df["risk_score"] = (
        risk_df["demand_pressure"] * 55 +
        risk_df["volatility"] * 30 +
        (1 / (risk_df["count"] + 1)) * 15
    )

    risk_df["risk_score"] = (
        risk_df["risk_score"] / risk_df["risk_score"].max() * 100
    ).round(2)

    stock_risk = (
        risk_df.sort_values("risk_score", ascending=False)
        .head(10)
        .rename(columns={category_col: "name"})
        [["name", "risk_score"]]
        .to_dict("records")
    )
    region_revenue = (
        df.groupby("region")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"region": "name"})
        .to_dict(orient="records")
    )

    category_revenue = (
        df.groupby("category")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"category": "name"})
        .to_dict(orient="records")
    )

    store_revenue = (
        df.groupby("store_id")["revenue"]
        .sum()
        .reset_index()
        .rename(columns={"store_id": "name"})
        .to_dict(orient="records")
    )

    return {
        "top_products": top_products,
        "stock_risk": stock_risk,
        "revenue_trend": revenue_trend,
        "region_revenue": region_revenue,
        "category_revenue": category_revenue,
        "store_revenue": store_revenue
    }
   
   
