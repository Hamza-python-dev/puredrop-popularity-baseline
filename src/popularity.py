"""Popularity baseline for PureDrop Dairy.

Popularity = how many DELIVERED order lines a product has.
One row in interactions.csv = one product on one customer's delivery on one date.
Rows with status 'skipped' or 'paused' (quantity 0, no amount) are not orders, so they are not counted.

Usage:  python src/popularity.py --data data/interactions.csv --k 5
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"product_id", "status"}


def load_interactions(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}. Put your Task 1 interactions.csv there.")
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"{path} is empty - nothing to count.")


def top_products(df, k=5):
    """Return the k most-ordered products as a DataFrame: rank, product_id, orders."""
    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive whole number, e.g. 5.")
    if df is None or len(df) == 0:
        raise ValueError("Interaction data is empty - nothing to count.")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Interaction data is missing required column(s): {sorted(missing)}.")

    status = df["status"].astype(str).str.strip().str.lower()
    delivered = df.loc[status == "delivered"].dropna(subset=["product_id"])
    if delivered.empty:
        raise ValueError("No delivered orders found - nothing to rank.")

    counts = delivered.groupby("product_id").size().reset_index(name="orders")
    counts = counts.sort_values(["orders", "product_id"], ascending=[False, True]).head(k)  # ties: lower id first
    counts.insert(0, "rank", range(1, len(counts) + 1))
    return counts.reset_index(drop=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="PureDrop Dairy popularity baseline")
    parser.add_argument("--data", default="data/interactions.csv")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args(argv)
    try:
        print(top_products(load_interactions(args.data), args.k).to_string(index=False))
    except (ValueError, FileNotFoundError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
