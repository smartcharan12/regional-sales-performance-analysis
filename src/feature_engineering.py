"""
Feature engineering: add analytical columns derived from the clean data.

A "feature" is a new column calculated from existing ones. We add columns
that make questions easier to answer, e.g. "Year" lets us group by year
without re-parsing dates in every query.

IMPORTANT - row-level vs. aggregated ratios
-------------------------------------------
'Profit Margin %' below is calculated per order line. It is useful for
filtering ("show me lines with negative margin") but you must NEVER average
it to get a region's margin. A region's margin is

    SUM(Profit) / SUM(Sales) x 100

because a $10 line and a $10,000 line should not count equally.
`aggregate_margin()` below does it the correct way.
"""

import numpy as np
import pandas as pd

DISCOUNT_BANDS = [-0.01, 0.0, 0.2, 0.4, 1.0]
DISCOUNT_LABELS = ["No discount", "1-20%", "21-40%", "Over 40%"]


def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
    """Split Order Date into parts used for grouping and time trends."""
    df = df.copy()
    d = df["Order Date"]
    df["Year"] = d.dt.year
    df["Quarter"] = "Q" + d.dt.quarter.astype(str)
    df["Month Number"] = d.dt.month
    df["Month"] = d.dt.strftime("%b")              # Jan, Feb ...
    df["Year-Month"] = d.dt.strftime("%Y-%m")      # 2024-01 (sorts correctly)
    # Shipping Days = Ship Date - Order Date (missing if Ship Date was invalid)
    df["Shipping Days"] = (df["Ship Date"] - d).dt.days.astype("Int64")
    return df


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Profit Margin % = Profit / Sales x 100
        How many cents of profit each $1 of sales keeps.
    Unit Price      = Sales / Quantity
        Average price actually paid per unit (after discount).
    Gross Sales     = Sales / (1 - Discount)
        What the line would have earned at full list price.
    Discount Amount = Gross Sales - Sales
        Revenue given away through discounting.
    """
    df = df.copy()
    df["Profit Margin %"] = (df["Profit"] / df["Sales"] * 100).round(2)
    df["Unit Price"] = (df["Sales"] / df["Quantity"]).round(2)
    df["Gross Sales"] = (df["Sales"] / (1 - df["Discount"])).round(2)
    df["Discount Amount"] = (df["Gross Sales"] - df["Sales"]).round(2)
    df["Is Loss"] = df["Profit"] < 0
    df["Discount Band"] = pd.cut(df["Discount"], bins=DISCOUNT_BANDS,
                                 labels=DISCOUNT_LABELS).astype(str)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all feature steps in order."""
    return add_financial_features(add_date_features(df))


def aggregate_margin(sales: pd.Series, profit: pd.Series) -> float:
    """Correct (weighted) margin for any group: total profit / total sales."""
    total_sales = sales.sum()
    return float(profit.sum() / total_sales * 100) if total_sales else np.nan
