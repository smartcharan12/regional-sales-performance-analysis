"""
Data cleaning for the RetailCo sales dataset.

Input : data/raw/sales_raw.csv       (messy export, one row per order line)
Output: a clean DataFrame + a cleaning log that records every decision

Design principles
-----------------
1. Fix before you delete. If a value can be reliably rebuilt from another
   column (Region from State, Customer Name from Customer ID), rebuild it.
2. Delete only what cannot be trusted AND cannot be rebuilt, and log it.
3. Never "invent" money. Missing Sales or Profit is not imputed, because a
   made-up number would flow straight into the KPIs.
4. Unusual is not the same as wrong. Large orders are flagged, not removed.
5. The order of steps matters. Text is standardised BEFORE duplicates are
   checked, so " West" and "West" do not hide a duplicate.
"""

import numpy as np
import pandas as pd

from utils import (STATE_TO_REGION, VALID_CATEGORIES, VALID_DISCOUNTS,
                   VALID_REGIONS)

TEXT_COLUMNS = ["Order ID", "Ship Mode", "Customer ID", "Customer Name",
                "Segment", "Country", "City", "State", "Region", "Product ID",
                "Category", "Sub-Category", "Product Name"]

# Known misspellings seen in the export -> correct value
REGION_FIXES = {"centrl": "Central"}
CATEGORY_FIXES = {"tech": "Technology"}


class CleaningLog:
    """Collects one entry per cleaning step so the process is auditable."""

    def __init__(self):
        self.entries = []

    def add(self, step, rows_before, rows_after, values_changed, decision):
        self.entries.append({
            "step": step,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "rows_removed": rows_before - rows_after,
            "values_changed": values_changed,
            "decision": decision,
        })

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.entries)


# ---------------------------------------------------------------------------
# Individual steps. Each takes a DataFrame and the log, returns a DataFrame.
# ---------------------------------------------------------------------------
def strip_whitespace(df, log):
    """Remove leading/trailing spaces: '  Boston ' -> 'Boston'."""
    df = df.copy()
    changed = 0
    for col in TEXT_COLUMNS:
        before = df[col]
        df[col] = df[col].str.strip()
        changed += int((before.notna() & (before != df[col])).sum())
    log.add("Strip whitespace", len(df), len(df), changed,
            "Trimmed spaces in text columns so identical values group together.")
    return df


def standardise_region(df, log):
    """
    Fix casing/typos in Region, then rebuild missing or wrong regions from
    State. State is the more reliable field: it is a fixed, validated list,
    and every state belongs to exactly one sales region.
    """
    df = df.copy()
    original = df["Region"].copy()
    cleaned = df["Region"].str.strip().str.lower()
    cleaned = cleaned.replace(REGION_FIXES).str.title()
    df["Region"] = cleaned

    expected = df["State"].map(STATE_TO_REGION)
    missing = int(df["Region"].isna().sum())
    mismatch = int((df["Region"].notna() & (df["Region"] != expected)).sum())
    df["Region"] = expected  # State is the source of truth

    changed = int((original.fillna("<NA>") != df["Region"].fillna("<NA>")).sum())
    log.add("Standardise Region", len(df), len(df), changed,
            f"Fixed casing/typos; rebuilt {missing} missing and {mismatch} "
            "inconsistent regions from State (each state maps to one region).")
    return df


def standardise_category(df, log):
    """
    Fix Category spelling. Category is rebuilt from Sub-Category, because each
    sub-category belongs to exactly one category (e.g. Phones -> Technology).
    """
    df = df.copy()
    original = df["Category"].copy()
    cleaned = df["Category"].str.strip().str.lower().replace(CATEGORY_FIXES).str.title()
    df["Category"] = cleaned

    # Build the Sub-Category -> Category lookup from rows that are already valid
    valid = df[df["Category"].isin(VALID_CATEGORIES)]
    lookup = valid.groupby("Sub-Category")["Category"].agg(lambda s: s.mode()[0])
    df["Category"] = df["Sub-Category"].map(lookup)

    changed = int((original != df["Category"]).sum())
    log.add("Standardise Category", len(df), len(df), changed,
            "Fixed casing/abbreviations; Category re-derived from Sub-Category.")
    return df


def remove_exact_duplicates(df, log):
    """
    Remove rows where EVERY column is identical. One order can contain many
    products, so a repeated Order ID is normal; a fully repeated row is not -
    it is the same line exported twice and would double-count revenue.
    """
    before = len(df)
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    log.add("Remove exact duplicates", before, len(df), before - len(df),
            "Dropped fully identical rows (double export). Kept first copy.")
    return df


def fix_numeric_types(df, log):
    """Convert Sales stored as text ('$1,234.50') into a real number."""
    df = df.copy()
    as_text = df["Sales"].astype(str)
    had_symbols = int(as_text.str.contains(r"[$,]", regex=True).sum())
    df["Sales"] = pd.to_numeric(as_text.str.replace(r"[$,]", "", regex=True), errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce")
    log.add("Fix numeric types", len(df), len(df), had_symbols,
            "Removed '$' and ',' from Sales text and converted numeric columns.")
    return df


def fix_discounts(df, log):
    """
    Discount must be a fraction between 0 and 1 (0.2 = 20%). Values like 20
    were typed as percentages; dividing by 100 gives a valid policy level, so
    they are corrected. Anything still invalid is removed.
    """
    df = df.copy()
    as_percent = df["Discount"] > 1
    corrected = df.loc[as_percent, "Discount"] / 100
    fixable = corrected.round(2).isin(VALID_DISCOUNTS)
    df.loc[corrected[fixable].index, "Discount"] = corrected[fixable]

    before = len(df)
    df = df[df["Discount"].round(2).isin(VALID_DISCOUNTS)].reset_index(drop=True)
    log.add("Fix discounts", before, len(df), int(fixable.sum()),
            "Converted percentage-style discounts (20 -> 0.20); removed values "
            "outside the allowed discount levels.")
    return df


def fill_names_from_ids(df, log):
    """
    A missing Customer Name is recoverable: the same Customer ID appears on
    other rows with the name filled in. Same for Product Name / Product ID.
    """
    df = df.copy()
    filled = 0
    for name_col, id_col in [("Customer Name", "Customer ID"), ("Product Name", "Product ID")]:
        lookup = df.dropna(subset=[name_col]).groupby(id_col)[name_col].first()
        missing = df[name_col].isna()
        df.loc[missing, name_col] = df.loc[missing, id_col].map(lookup)
        filled += int(missing.sum() - df[name_col].isna().sum())
    log.add("Fill names from IDs", len(df), len(df), filled,
            "Rebuilt missing Customer/Product names using their IDs.")
    return df


def fix_dates(df, log):
    """
    Order Date is essential (time trends, YoY growth). If it cannot be parsed
    the row cannot be placed in time, so it is removed.
    Ship Date only affects the shipping-time analysis. If it is earlier than
    the Order Date (impossible), the SALE is still real - so we keep the row
    and blank out only the Ship Date.
    """
    df = df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%Y-%m-%d", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%Y-%m-%d", errors="coerce")

    before = len(df)
    df = df.dropna(subset=["Order Date"]).reset_index(drop=True)
    log.add("Remove invalid order dates", before, len(df), before - len(df),
            "Dropped rows whose Order Date is not a real date (e.g. 2023-02-30).")

    bad_ship = df["Ship Date"] < df["Order Date"]
    df.loc[bad_ship, "Ship Date"] = pd.NaT
    log.add("Blank impossible ship dates", len(df), len(df), int(bad_ship.sum()),
            "Ship Date before Order Date set to missing; sale itself kept.")
    return df


def remove_missing_money(df, log):
    """
    Sales or Profit missing: there is no reliable way to rebuild them (the
    list price and cost are not in the data). Filling with an average would
    invent revenue, so these rows are removed and the count is logged.
    """
    before = len(df)
    df = df.dropna(subset=["Sales", "Profit"]).reset_index(drop=True)
    log.add("Remove missing Sales/Profit", before, len(df), before - len(df),
            "Cannot rebuild money values without price/cost data; rows removed.")
    return df


def remove_invalid_values(df, log):
    """
    Sales <= 0 or Quantity <= 0 is impossible for a normal sale. Returns would
    be recorded in a separate returns table, so these are data-entry errors.
    Note: negative PROFIT is valid (a loss-making sale) and is kept.
    """
    before = len(df)
    df = df[(df["Sales"] > 0) & (df["Quantity"] > 0)].reset_index(drop=True)
    df["Quantity"] = df["Quantity"].astype(int)
    log.add("Remove impossible Sales/Quantity", before, len(df), before - len(df),
            "Removed Sales <= 0 or Quantity <= 0. Negative Profit is kept (real losses).")
    return df


def flag_outliers(df, log):
    """
    Flag (do NOT remove) unusually large order lines using the IQR rule:
    a value is an outlier if it is above Q3 + 1.5 x IQR.
    Large lines here are copiers, machines and furniture - genuine revenue.
    Removing them would understate Technology and Furniture sales.
    """
    df = df.copy()
    q1, q3 = df["Sales"].quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    df["Is High Value"] = df["Sales"] > upper
    log.add("Flag high-value outliers", len(df), len(df), int(df["Is High Value"].sum()),
            f"Flagged lines with Sales > {upper:,.2f} (IQR rule). Kept: they are real large orders.")
    return df


def check_duplicate_order_lines(df, log):
    """
    Order ID repeats are expected (several products per order). But the same
    product twice in one order would suggest a hidden duplicate. Report it.
    """
    dup = int(df.duplicated(subset=["Order ID", "Product ID"]).sum())
    log.add("Check Order ID + Product ID", len(df), len(df), dup,
            "Repeated Order IDs are normal (multi-product orders); "
            f"{dup} repeated Order ID + Product ID pairs found.")
    return df


def validate(df: pd.DataFrame) -> None:
    """Final safety checks. If any fails, the pipeline stops loudly."""
    assert df["Region"].isin(VALID_REGIONS).all(), "Unexpected Region value"
    assert df["Category"].isin(VALID_CATEGORIES).all(), "Unexpected Category value"
    assert df[["Customer Name", "Product Name", "Sales", "Profit", "Order Date"]].notna().all().all()
    assert (df["Sales"] > 0).all() and (df["Quantity"] > 0).all()
    assert df["Discount"].between(0, 1).all()
    assert not df.duplicated().any()


def count_repaired_values(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.Series:
    """
    Count, per column, how many values in the FINAL clean data differ from the
    raw export. Each cell is counted once, even if several steps touched it
    (e.g. ' east ' is trimmed AND re-cased). The cleaning log counts changes
    per step, so its total is higher; this is the number to quote.
    """
    original = [c for c in raw.columns if c in clean.columns]
    key = ["Order ID", "Product ID"]
    raw_first = raw.drop_duplicates().drop_duplicates(subset=key)
    m = clean[original].merge(raw_first[original], on=key, how="left", suffixes=("", "_raw"))
    counts = {}
    for col in original:
        if col in key:
            continue
        new, old = m[col], m[f"{col}_raw"]
        if pd.api.types.is_numeric_dtype(new):
            old_num = pd.to_numeric(old.astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
            # a '$1,277.10' text value counts as repaired even though the number is equal
            was_text = pd.to_numeric(old, errors="coerce").isna() & old.notna()
            changed = ~np.isclose(new, old_num, equal_nan=False) | was_text
        else:
            changed = new.astype(str).where(new.notna(), "<NA>") != old.astype(str).where(old.notna(), "<NA>")
        counts[col] = int(changed.sum())
    s = pd.Series(counts)
    return s[s > 0]


def clean_sales_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run every cleaning step in order. Returns (clean_df, cleaning_log)."""
    log = CleaningLog()
    df = raw.copy()
    log.add("Load raw data", len(df), len(df), 0, "Starting point.")

    df = strip_whitespace(df, log)
    df = standardise_region(df, log)
    df = standardise_category(df, log)
    df = fix_numeric_types(df, log)
    df = remove_exact_duplicates(df, log)
    df = fix_discounts(df, log)
    df = fill_names_from_ids(df, log)
    df = fix_dates(df, log)
    df = remove_missing_money(df, log)
    df = remove_invalid_values(df, log)
    df = check_duplicate_order_lines(df, log)
    df = flag_outliers(df, log)

    validate(df)
    log.add("Final clean data", len(df), len(df), 0, "All validation checks passed.")
    return df, log.to_frame()


if __name__ == "__main__":
    from utils import RAW_FILE
    raw_df = pd.read_csv(RAW_FILE)
    clean_df, log_df = clean_sales_data(raw_df)
    pd.set_option("display.width", 200, "display.max_colwidth", 90)
    print(log_df[["step", "rows_before", "rows_after", "rows_removed", "values_changed"]])
    print(f"\nRaw rows: {len(raw_df):,}  ->  Clean rows: {len(clean_df):,}")
