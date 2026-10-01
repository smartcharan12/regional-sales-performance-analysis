r"""
Split the clean flat table into a star schema for Power BI.

Star schema = one FACT table (the events we measure: order lines, with
numbers like Sales and Profit) surrounded by DIMENSION tables (the
descriptions we filter by: who, what, where, when).

    DimDate  DimCustomer  DimProduct  DimGeography
         \        |           |          /
                    FactSales

Why not keep one big flat table?
  * Each customer/product description is stored once, not on every row.
  * Filters flow in one clear direction (dimension -> fact).
  * DAX time intelligence (SAMEPERIODLASTYEAR etc.) needs a proper,
    continuous date table.
  * It is the modelling style Power BI's engine is optimised for.

Output: CSV files in data/processed/powerbi/
"""

import pandas as pd

from utils import POWERBI_EXPORT


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """Continuous calendar covering every day of every year in the data.
    No gaps are allowed: time-intelligence functions need complete years."""
    start = pd.Timestamp(year=df["Order Date"].dt.year.min(), month=1, day=1)
    end = pd.Timestamp(year=df["Order Date"].dt.year.max(), month=12, day=31)
    d = pd.DataFrame({"Date": pd.date_range(start, end, freq="D")})
    d["DateKey"] = d["Date"].dt.strftime("%Y%m%d").astype(int)
    d["Year"] = d["Date"].dt.year
    d["Quarter"] = "Q" + d["Date"].dt.quarter.astype(str)
    d["Month Number"] = d["Date"].dt.month
    d["Month"] = d["Date"].dt.strftime("%b")
    d["Year-Month"] = d["Date"].dt.strftime("%Y-%m")
    d["Weekday"] = d["Date"].dt.strftime("%a")
    d["Is Weekend"] = d["Date"].dt.dayofweek >= 5
    return d[["DateKey", "Date", "Year", "Quarter", "Month Number", "Month",
              "Year-Month", "Weekday", "Is Weekend"]]


def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    return (df[["Customer ID", "Customer Name", "Segment"]]
            .drop_duplicates("Customer ID").sort_values("Customer ID"))


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    return (df[["Product ID", "Product Name", "Category", "Sub-Category"]]
            .drop_duplicates("Product ID").sort_values("Product ID"))


def build_dim_geography(df: pd.DataFrame) -> pd.DataFrame:
    """One row per City + State (city names can repeat across states).
    A surrogate integer key is created because there is no natural ID."""
    geo = (df[["Country", "Region", "State", "City"]].drop_duplicates()
           .sort_values(["Region", "State", "City"]).reset_index(drop=True))
    geo.insert(0, "GeoKey", geo.index + 1)
    return geo


def build_fact_sales(df: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    fact = df.merge(geo[["GeoKey", "State", "City"]], on=["State", "City"], how="left")
    assert fact["GeoKey"].notna().all(), "Every sale must map to a geography row"
    fact["OrderDateKey"] = fact["Order Date"].dt.strftime("%Y%m%d").astype(int)
    fact.insert(0, "SalesKey", range(1, len(fact) + 1))
    return fact[["SalesKey", "Order ID", "OrderDateKey", "Order Date", "Ship Date",
                 "Ship Mode", "Customer ID", "Product ID", "GeoKey", "Sales",
                 "Quantity", "Discount", "Profit", "Gross Sales", "Discount Amount",
                 "Shipping Days"]]


def build_star_schema(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    geo = build_dim_geography(df)
    tables = {
        "DimDate": build_dim_date(df),
        "DimCustomer": build_dim_customer(df),
        "DimProduct": build_dim_product(df),
        "DimGeography": geo,
        "FactSales": build_fact_sales(df, geo),
    }
    # Integrity checks: every key in the fact table exists in its dimension
    fact = tables["FactSales"]
    assert fact["Customer ID"].isin(tables["DimCustomer"]["Customer ID"]).all()
    assert fact["Product ID"].isin(tables["DimProduct"]["Product ID"]).all()
    assert fact["OrderDateKey"].isin(tables["DimDate"]["DateKey"]).all()
    assert len(fact) == len(df), "Star schema must not add or lose rows"
    return tables


def export_star_schema(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    POWERBI_EXPORT.mkdir(parents=True, exist_ok=True)
    tables = build_star_schema(df)
    for name, table in tables.items():
        table.to_csv(POWERBI_EXPORT / f"{name}.csv", index=False, date_format="%Y-%m-%d",
                     lineterminator="\n")  # same file on Windows and Linux (MySQL LOAD DATA expects \n)
    return tables
