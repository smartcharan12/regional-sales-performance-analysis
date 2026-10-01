"""
Run the whole project end to end, from raw data to charts:

    python src/pipeline.py              # use existing data/raw/sales_raw.csv
    python src/pipeline.py --regenerate # rebuild the raw file first (same seed = same data)

Steps: (generate) -> clean -> feature engineering -> save clean CSV
       -> export star schema for Power BI -> save all EDA charts
"""

import argparse

import pandas as pd

import generate_data
from build_star_schema import export_star_schema
from data_cleaning import clean_sales_data, count_repaired_values
from eda import kpi_summary, save_all_charts
from feature_engineering import engineer_features
from utils import CLEAN_FILE, CLEANING_LOG_FILE, RAW_FILE


def main(regenerate: bool = False) -> None:
    if regenerate or not RAW_FILE.exists():
        print("1. Generating raw data ...")
        generate_data.main()

    print("2. Cleaning ...")
    raw = pd.read_csv(RAW_FILE)
    clean, log = clean_sales_data(raw)
    print(f"   raw rows {len(raw):,} -> clean rows {len(clean):,}; "
          f"values repaired: {count_repaired_values(raw, clean).sum()}")

    print("3. Feature engineering ...")
    clean = engineer_features(clean)
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(CLEAN_FILE, index=False, date_format="%Y-%m-%d", lineterminator="\n")
    log.to_csv(CLEANING_LOG_FILE, index=False, lineterminator="\n")
    print(f"   saved {CLEAN_FILE.name} ({clean.shape[1]} columns)")

    print("4. Exporting star schema for Power BI ...")
    tables = export_star_schema(clean)
    for name, t in tables.items():
        print(f"   {name:<13} {len(t):>6,} rows")

    print("5. Saving charts ...")
    save_all_charts(clean)

    print("\nHeadline KPIs")
    for k, v in kpi_summary(clean).items():
        print(f"   {k:<32} {v:>14,.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--regenerate", action="store_true",
                        help="rebuild data/raw/sales_raw.csv before running")
    main(parser.parse_args().regenerate)
