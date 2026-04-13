"""
preprocess.py — Run once to build the joblib cache.
Usage: uv run python preprocess.py
"""

from pathlib import Path
import pandas as pd
import joblib

DATA_PATH = Path(__file__).parent / "Online Retail.xlsx"
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

def main():
    print("📦 Reading Excel file…")
    df = pd.read_excel(DATA_PATH, dtype={"CustomerID": str})
    df.columns = df.columns.str.strip()

    print("🧹 Cleaning data…")
    df = df[df["CustomerID"].notna()]
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df = df.drop_duplicates(subset=["InvoiceNo", "StockCode", "Quantity"])

    print("🔢 Building cohort index…")
    df["CohortDate"] = (
        df.groupby("CustomerID")["InvoiceDate"]
        .transform("min")
        .dt.to_period("M")
    )
    df["InvoicePeriod"] = df["InvoiceDate"].dt.to_period("M")
    df["CohortIndex"] = (
        (df["InvoicePeriod"].dt.year - df["CohortDate"].dt.year) * 12
        + (df["InvoicePeriod"].dt.month - df["CohortDate"].dt.month)
        + 1
    )

    print("📊 Building pivot tables…")
    cohort_pivot = (
        df.groupby(["CohortDate", "CohortIndex"])["CustomerID"]
        .nunique()
        .unstack("CohortIndex")
    )
    cohort_size = cohort_pivot[1]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100

    print("💾 Saving to .cache/…")
    joblib.dump(df,            CACHE_DIR / "df.joblib")
    joblib.dump(cohort_pivot,  CACHE_DIR / "cohort_pivot.joblib")
    joblib.dump(retention,     CACHE_DIR / "retention.joblib")
    joblib.dump(cohort_size,   CACHE_DIR / "cohort_size.joblib")

    print(f"✅ Done. Cached {len(df):,} rows across {len(cohort_size)} cohorts.")
    print(f"   Files written to {CACHE_DIR.resolve()}")

if __name__ == "__main__":
    main()
