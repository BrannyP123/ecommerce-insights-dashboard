"""
clean_data.py

Cleans the raw Online Retail dataset and saves a analysis-ready CSV.
Run this once before starting the app: python clean_data.py
"""
import pandas as pd

RAW_PATH = "online_retail.csv"
CLEAN_PATH = "clean_retail.csv.gz"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Parse dates
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Drop rows with no customer ID -- we can't attribute these to a customer,
    # and they're not useful for customer-level analysis (~25% of rows).
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)

    # Drop rows with missing product descriptions
    df = df.dropna(subset=["Description"])
    df["Description"] = df["Description"].str.strip()

    # Flag and separate cancellations (InvoiceNo starting with "C")
    df["IsCancelled"] = df["InvoiceNo"].astype(str).str.startswith("C")

    # Remove bad rows: non-positive price, and non-cancellation rows with
    # non-positive quantity (these are typically data entry errors, not
    # legitimate transactions or cancellations)
    df = df[df["UnitPrice"] > 0]
    df = df[(df["Quantity"] > 0) | (df["IsCancelled"])]

    # Compute revenue line item
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    # Add useful date parts
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["Weekday"] = df["InvoiceDate"].dt.day_name()

    return df


if __name__ == "__main__":
    raw = pd.read_csv(RAW_PATH)
    print(f"Raw rows: {len(raw):,}")

    cleaned = clean(raw)
    print(f"Cleaned rows: {len(cleaned):,}")
    print(f"Dropped: {len(raw) - len(cleaned):,} rows")

    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"Saved cleaned data to {CLEAN_PATH}")
