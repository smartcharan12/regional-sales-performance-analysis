"""
Exploratory Data Analysis (EDA): reusable summary tables and charts.

Two kinds of functions live here:
  * summary functions  -> return a pandas DataFrame (the numbers)
  * chart functions     -> draw one chart and save it to visualizations/

Every chart answers one named business question (see the docstrings).
Notebooks 03 and 04 call these functions, so the logic is written once and
the notebooks stay readable.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter, MaxNLocator

from feature_engineering import aggregate_margin
from utils import (CATEGORY_COLORS, INK_SECONDARY, LOSS, MUTED, PRIMARY,
                   REGION_COLORS, VIZ_DIR, money, set_chart_style)

MONEY_AXIS = FuncFormatter(lambda v, _: money(v))
PCT_AXIS = FuncFormatter(lambda v, _: f"{v:.0f}%")
# Diverging scale for profit: red = loss, grey = break-even, blue = profit
PROFIT_CMAP = LinearSegmentedColormap.from_list(
    "profit", ["#b3302f", "#e98a86", "#f0efec", "#86b6ef", "#1c5cab"])


# ===========================================================================
# Summary tables
# ===========================================================================
def kpi_summary(df: pd.DataFrame) -> pd.Series:
    """Headline KPIs for the whole dataset (or any filtered slice)."""
    orders = df["Order ID"].nunique()
    latest = df["Year"].max()
    cur, prev = df[df["Year"] == latest], df[df["Year"] == latest - 1]
    return pd.Series({
        "Total Sales": df["Sales"].sum(),
        "Total Profit": df["Profit"].sum(),
        "Profit Margin %": aggregate_margin(df["Sales"], df["Profit"]),
        "Total Orders": orders,
        "Total Quantity": df["Quantity"].sum(),
        "Average Order Value": df["Sales"].sum() / orders,
        "Customers": df["Customer ID"].nunique(),
        f"YoY Sales Growth % ({latest})": (cur["Sales"].sum() / prev["Sales"].sum() - 1) * 100,
        f"YoY Profit Growth % ({latest})": (cur["Profit"].sum() / prev["Profit"].sum() - 1) * 100,
    })


def summarize_by(df: pd.DataFrame, by) -> pd.DataFrame:
    """Sales, profit, quantity, orders, margin and sales share for each group."""
    out = df.groupby(by).agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Gross_Sales=("Gross Sales", "sum"),
        Discount_Amount=("Discount Amount", "sum"),
    )
    out["Profit Margin %"] = out["Profit"] / out["Sales"] * 100
    out["Sales Share %"] = out["Sales"] / out["Sales"].sum() * 100
    # Effective discount rate = revenue given away / revenue at list price
    out["Effective Discount %"] = out["Discount_Amount"] / out["Gross_Sales"] * 100
    out = out.drop(columns=["Gross_Sales", "Discount_Amount"])
    return out.sort_values("Sales", ascending=False).round(2)


def yearly_pivot(df: pd.DataFrame, by: str, value: str = "Sales") -> pd.DataFrame:
    """Rows = groups, columns = years, plus growth of latest year vs previous
    and the compound annual growth rate (CAGR) over the whole period."""
    pivot = df.pivot_table(index=by, columns="Year", values=value, aggfunc="sum")
    first, last = pivot.columns.min(), pivot.columns.max()
    pivot[f"YoY % ({last})"] = (pivot[last] / pivot[last - 1] - 1) * 100
    pivot[f"CAGR % ({first}-{last})"] = ((pivot[last] / pivot[first]) ** (1 / (last - first)) - 1) * 100
    return pivot.round(2)


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit for every calendar month, in time order."""
    out = df.groupby("Year-Month")[["Sales", "Profit"]].sum()
    out.index = pd.PeriodIndex(out.index, freq="M")
    return out


def seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Average sales per calendar month across all years (Jan..Dec)."""
    monthly = df.groupby(["Year", "Month Number"])["Sales"].sum().reset_index()
    out = monthly.groupby("Month Number")["Sales"].mean().to_frame("Avg Monthly Sales")
    out["Index vs Average"] = out["Avg Monthly Sales"] / out["Avg Monthly Sales"].mean() * 100
    return out.round(1)


def top_n(df: pd.DataFrame, by: str, metric: str = "Sales", n: int = 10,
          ascending: bool = False) -> pd.DataFrame:
    """Top (or bottom) n members of a column by a metric."""
    out = summarize_by(df, by)[["Sales", "Profit", "Profit Margin %", "Orders"]]
    return out.sort_values(metric, ascending=ascending).head(n)


def high_sales_low_profit(df: pd.DataFrame, by: str = "Product Name",
                          sales_quantile: float = 0.75,
                          max_margin: float = 5.0) -> pd.DataFrame:
    """
    Items in the top 25% by sales whose margin is below 5%.
    These look successful on a sales report but contribute little or no profit.
    Thresholds are parameters so they can be challenged and changed.
    """
    s = summarize_by(df, by)
    cutoff = s["Sales"].quantile(sales_quantile)
    flagged = s[(s["Sales"] >= cutoff) & (s["Profit Margin %"] < max_margin)]
    return flagged[["Sales", "Profit", "Profit Margin %", "Effective Discount %"]].sort_values("Profit")


def discount_impact(df: pd.DataFrame, by: str = "Discount") -> pd.DataFrame:
    """Profitability at each discount level."""
    out = df.groupby(by).agg(
        Lines=("Sales", "size"),
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Loss_Lines=("Is Loss", "sum"),
    )
    out["Profit Margin %"] = out["Profit"] / out["Sales"] * 100
    out["% Lines Loss-Making"] = out["Loss_Lines"] / out["Lines"] * 100
    return out.drop(columns="Loss_Lines").round(2)


def discount_correlation(df: pd.DataFrame) -> pd.Series:
    """
    Correlation between Discount and line-level Profit Margin %.
    Pearson measures a straight-line relationship; Spearman measures any
    consistently increasing/decreasing (monotonic) relationship.
    Correlation shows association, NOT cause.
    """
    return pd.Series({
        "Pearson": df["Discount"].corr(df["Profit Margin %"], method="pearson"),
        # Spearman = Pearson correlation of the ranks (avoids needing scipy)
        "Spearman": df["Discount"].rank().corr(df["Profit Margin %"].rank()),
    }).round(3)


def region_subcategory_profit(df: pd.DataFrame) -> pd.DataFrame:
    """Profit for every Region x Sub-Category combination (profitability matrix)."""
    return df.pivot_table(index="Sub-Category", columns="Region", values="Profit",
                          aggfunc="sum").round(0)


# ===========================================================================
# Charts - each saves a PNG and returns the figure
# ===========================================================================
def _save(fig, name):
    VIZ_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(VIZ_DIR / name)
    return fig


def _label_bars(ax, values, fmt, horizontal=True):
    """Write the value at the end of each bar (selective, readable labels)."""
    for i, v in enumerate(values):
        if horizontal:
            ax.text(v, i, f"  {fmt(v)}", va="center",
                    ha="left" if v >= 0 else "right", color=INK_SECONDARY, fontsize=9)
        else:
            ax.text(i, v, fmt(v), ha="center", va="bottom" if v >= 0 else "top",
                    color=INK_SECONDARY, fontsize=9)


def plot_sales_by_region(df):
    """Q1: Which region generates the highest sales? (bar: compare categories)"""
    s = summarize_by(df, "Region").sort_values("Sales")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.barh(s.index, s["Sales"], color=PRIMARY, height=0.6)
    _label_bars(ax, s["Sales"], money)
    ax.xaxis.set_major_formatter(MONEY_AXIS)
    ax.set_title("Total sales by region, 2021-2024")
    ax.set_xlabel("Sales")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, s["Sales"].max() * 1.15)
    return _save(fig, "sales_by_region.png")


def plot_profit_by_region(df):
    """Q2: Which region generates the highest profit?"""
    s = summarize_by(df, "Region").sort_values("Profit")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    colors = [LOSS if v < 0 else PRIMARY for v in s["Profit"]]
    ax.barh(s.index, s["Profit"], color=colors, height=0.6)
    _label_bars(ax, s["Profit"], money)
    ax.xaxis.set_major_formatter(MONEY_AXIS)
    ax.set_title("Total profit by region, 2021-2024")
    ax.set_xlabel("Profit")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(min(0, s["Profit"].min() * 1.2), s["Profit"].max() * 1.18)
    return _save(fig, "profit_by_region.png")


def plot_regional_profit_margin(df):
    """Q3: Which region keeps the most profit per $ of sales? Reference line = company margin."""
    s = summarize_by(df, "Region").sort_values("Profit Margin %")
    overall = aggregate_margin(df["Sales"], df["Profit"])
    fig, ax = plt.subplots(figsize=(9, 4.2))
    colors = [MUTED if v >= overall else LOSS for v in s["Profit Margin %"]]
    ax.barh(s.index, s["Profit Margin %"], color=colors, height=0.6)
    _label_bars(ax, s["Profit Margin %"], lambda v: f"{v:.1f}%")
    ax.axvline(overall, color=INK_SECONDARY, linewidth=1)
    ax.xaxis.set_major_formatter(PCT_AXIS)
    ax.set_title(f"Profit margin by region (line = company margin {overall:.1f}%; red = below it)")
    ax.set_xlabel("Profit margin (total profit / total sales)")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, s["Profit Margin %"].max() * 1.2)
    return _save(fig, "regional_profit_margin.png")


def plot_monthly_sales(df):
    """Q9/Q10: How are sales changing over time? Monthly line + 12-month rolling average."""
    m = monthly_trend(df)
    x = m.index.to_timestamp()
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(x, m["Sales"], color=MUTED, linewidth=1.5, label="Monthly sales")
    ax.plot(x, m["Sales"].rolling(12).mean(), color=PRIMARY, linewidth=2.2,
            label="12-month rolling average (trend)")
    ax.yaxis.set_major_formatter(MONEY_AXIS)
    ax.set_title("Monthly sales with 12-month rolling average")
    ax.set_ylabel("Sales")
    ax.set_ylim(0)
    ax.legend(loc="upper left")
    return _save(fig, "monthly_sales.png")


def plot_seasonality(df):
    """Q9: Which months have the highest sales? (average across years, so one big year cannot dominate)"""
    s = seasonality(df)
    labels = pd.to_datetime(s.index, format="%m").strftime("%b")
    top3 = s["Avg Monthly Sales"].nlargest(3).index
    colors = [PRIMARY if m in top3 else MUTED for m in s.index]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.bar(labels, s["Avg Monthly Sales"], color=colors, width=0.65)
    ax.yaxis.set_major_formatter(MONEY_AXIS)
    ax.set_title("Average sales by calendar month (top 3 months highlighted)")
    ax.set_ylabel("Average sales per month")
    ax.grid(axis="x", visible=False)
    return _save(fig, "seasonality.png")


def plot_yearly_sales_by_region(df):
    """Q8/Q11: Which regions are growing or declining? One line per region."""
    p = df.pivot_table(index="Year", columns="Region", values="Sales", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(10, 5))
    for region in p.columns:
        ax.plot(p.index, p[region], marker="o", markersize=6, linewidth=2,
                color=REGION_COLORS[region], label=region)
        ax.text(p.index[-1] + 0.06, p[region].iloc[-1], region, va="center",
                color=INK_SECONDARY, fontsize=9)
    ax.set_xticks(p.index)
    ax.yaxis.set_major_formatter(MONEY_AXIS)
    ax.set_ylim(0)
    ax.set_xlim(p.index.min() - 0.2, p.index.max() + 0.45)
    ax.set_title("Yearly sales by region")
    ax.set_ylabel("Sales")
    ax.legend(loc="lower left", ncol=4)
    return _save(fig, "yearly_sales_by_region.png")


def plot_category_analysis(df):
    """Q4/Q5: Which category drives revenue vs. profit? Two panels, same order (no dual axis)."""
    s = summarize_by(df, "Category").sort_values("Sales")
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), sharey=True)
    panels = [("Sales", money, MONEY_AXIS), ("Profit", money, MONEY_AXIS),
              ("Profit Margin %", lambda v: f"{v:.1f}%", PCT_AXIS)]
    for ax, (col, fmt, axis_fmt) in zip(axes, panels):
        colors = [LOSS if v < 0 else PRIMARY for v in s[col]]
        ax.barh(s.index, s[col], color=colors, height=0.55)
        _label_bars(ax, s[col], fmt)
        ax.axvline(0, color=MUTED, linewidth=1)
        ax.xaxis.set_major_formatter(axis_fmt)
        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.set_title(col)
        ax.grid(axis="y", visible=False)
        lo, hi = min(0, s[col].min()), max(0, s[col].max())
        ax.set_xlim(lo * 1.6 if lo < 0 else 0, hi * 1.45)
    fig.suptitle("Category performance: revenue leader is not the same as margin leader",
                 fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "category_analysis.png")


def plot_subcategory_profit(df):
    """Q12/Q13: Which sub-categories make or lose money?"""
    s = summarize_by(df, "Sub-Category").sort_values("Profit")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    colors = [LOSS if v < 0 else PRIMARY for v in s["Profit"]]
    ax.barh(s.index, s["Profit"], color=colors, height=0.65)
    _label_bars(ax, s["Profit"], money)
    ax.axvline(0, color=INK_SECONDARY, linewidth=1)
    ax.xaxis.set_major_formatter(MONEY_AXIS)
    ax.set_xlim(s["Profit"].min() * 1.35, s["Profit"].max() * 1.2)
    ax.set_title("Total profit by sub-category (red = loss-making)")
    ax.set_xlabel("Profit")
    ax.grid(axis="y", visible=False)
    return _save(fig, "subcategory_profit.png")


def plot_discount_vs_margin(df):
    """Q8: How does discount level relate to profitability? Aggregated margin per discount level."""
    d = discount_impact(df)
    labels = [f"{x:.0%}" for x in d.index]
    colors = [LOSS if v < 0 else PRIMARY for v in d["Profit Margin %"]]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar(labels, d["Profit Margin %"], color=colors, width=0.65)
    _label_bars(ax, d["Profit Margin %"], lambda v: f"{v:.0f}%", horizontal=False)
    ax.axhline(0, color=INK_SECONDARY, linewidth=1)
    ax.yaxis.set_major_formatter(PCT_AXIS)
    ax.set_title("Profit margin at each discount level")
    ax.set_xlabel("Discount given on the order line")
    ax.set_ylabel("Profit margin")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(d["Profit Margin %"].min() * 1.15, d["Profit Margin %"].max() * 1.25)
    return _save(fig, "discount_vs_margin.png")


def plot_region_subcategory_heatmap(df):
    """Q15: Where exactly is profit lost? Region x Sub-Category profitability matrix."""
    p = region_subcategory_profit(df) / 1000
    p = p.loc[p.sum(axis=1).sort_values().index]
    lim = np.abs(p.values).max()
    fig, ax = plt.subplots(figsize=(8.5, 8))
    sns.heatmap(p, cmap=PROFIT_CMAP, center=0, vmin=-lim, vmax=lim, annot=True,
                fmt=".1f", linewidths=2, linecolor="#fcfcfb",
                cbar_kws={"label": "Profit ($ thousands)"}, ax=ax)
    ax.set_title("Profit ($K) by sub-category and region\nred = loss, blue = profit")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.grid(False)
    return _save(fig, "region_subcategory_profit_heatmap.png")


def plot_top_customers(df, n=10):
    """Q7: Which customers contribute the most revenue?"""
    t = top_n(df, "Customer Name", n=n).sort_values("Sales")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(t.index, t["Sales"], color=PRIMARY, height=0.6)
    _label_bars(ax, t["Sales"], money)
    ax.xaxis.set_major_formatter(MONEY_AXIS)
    ax.set_xlim(0, t["Sales"].max() * 1.18)
    ax.set_title(f"Top {n} customers by sales, 2021-2024")
    ax.grid(axis="y", visible=False)
    return _save(fig, "top_customers.png")


def plot_segment_performance(df):
    """Q14: Which customer segment generates the most sales, and at what margin?"""
    s = summarize_by(df, "Segment").sort_values("Sales")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
    for ax, col, fmt, axis_fmt in [(axes[0], "Sales", money, MONEY_AXIS),
                                   (axes[1], "Profit Margin %", lambda v: f"{v:.1f}%", PCT_AXIS)]:
        ax.barh(s.index, s[col], color=PRIMARY, height=0.55)
        _label_bars(ax, s[col], fmt)
        ax.xaxis.set_major_formatter(axis_fmt)
        ax.set_xlim(0, s[col].max() * 1.3)
        ax.set_title(col)
        ax.grid(axis="y", visible=False)
    fig.suptitle("Customer segment performance", fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "segment_performance.png")


def plot_product_sales_vs_profit(df):
    """Q6: Which products have high sales but low profit? Each dot = one product."""
    s = summarize_by(df, "Product Name")
    flagged = high_sales_low_profit(df).index
    cutoff = s["Sales"].quantile(0.75)
    fig, ax = plt.subplots(figsize=(10, 6))
    normal = s[~s.index.isin(flagged)]
    hit = s[s.index.isin(flagged)]
    ax.scatter(normal["Sales"], normal["Profit"], s=22, color=MUTED, label="Other products")
    ax.scatter(hit["Sales"], hit["Profit"], s=34, color=LOSS, edgecolor="#fcfcfb",
               linewidth=1.2, label="Top-25% sales but margin < 5%")
    ax.axhline(0, color=INK_SECONDARY, linewidth=1)
    ax.axvline(cutoff, color=INK_SECONDARY, linewidth=0.8)
    ax.text(cutoff, ax.get_ylim()[1], " top-25% sales threshold", va="top",
            color=INK_SECONDARY, fontsize=9)
    ax.xaxis.set_major_formatter(MONEY_AXIS)
    ax.yaxis.set_major_formatter(MONEY_AXIS)
    ax.set_title("Product sales vs. profit (each dot is one product)")
    ax.set_xlabel("Total sales")
    ax.set_ylabel("Total profit")
    ax.legend(loc="upper left")
    return _save(fig, "product_sales_vs_profit.png")


ALL_CHARTS = [
    plot_sales_by_region, plot_profit_by_region, plot_regional_profit_margin,
    plot_monthly_sales, plot_seasonality, plot_yearly_sales_by_region,
    plot_category_analysis, plot_subcategory_profit, plot_discount_vs_margin,
    plot_region_subcategory_heatmap, plot_top_customers,
    plot_segment_performance, plot_product_sales_vs_profit,
]


def save_all_charts(df: pd.DataFrame) -> None:
    set_chart_style()
    for chart in ALL_CHARTS:
        fig = chart(df)
        plt.close(fig)
