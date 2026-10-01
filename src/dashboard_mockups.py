"""
Render DESIGN MOCKUPS of the 5 Power BI dashboard pages (+ the hidden Region
Detail page) with matplotlib, using the real project data.

    python src/dashboard_mockups.py      -> powerbi/mockups/*.png

IMPORTANT - what these images are, and are not
----------------------------------------------
* They ARE a preview of the layout in powerbi/Dashboard_Design.md, with every
  number computed from data/processed/sales_cleaned.csv. That makes them a
  visual reference for what each Power BI page should show.
* They are NOT Power BI screenshots. Power BI Desktop is Windows-only and was
  not available when this was built. Every image carries a visible
  "DESIGN MOCKUP" banner. Real screenshots belong in screenshots/ and can only
  come from the finished .pbix.
"""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch

from eda import (discount_impact, high_sales_low_profit, region_subcategory_profit,
                 summarize_by, top_n)
from feature_engineering import aggregate_margin
from utils import (CLEAN_FILE, GRID, INK, INK_SECONDARY, LOSS, MUTED, PRIMARY,
                   PROJECT_ROOT, REGION_COLORS, money, set_chart_style)

OUT_DIR = PROJECT_ROOT / "powerbi" / "mockups"
BELOW = "#EC835A"          # "below company margin" (same as the DAX Margin Color)
CANVAS = "#FCFCFB"
CARD_BG = "#FFFFFF"
PROFIT_CMAP = LinearSegmentedColormap.from_list(
    "profit", ["#b3302f", "#e98a86", "#f0efec", "#86b6ef", "#1c5cab"])
BANNER = ("DESIGN MOCKUP: rendered in Python (matplotlib) from the project data to preview the "
          "Power BI layout. Not a Power BI screenshot.")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def margin_color(margin, company):
    """Same rule as the DAX measure [Margin Color]."""
    if margin < 0:
        return LOSS
    return BELOW if margin < company else PRIMARY


def card_money(v):
    """Card format used in the dashboard spec: $1.19M, $110.24K."""
    sign = "-" if v < 0 else ""
    v = abs(v)
    return f"{sign}${v / 1e6:,.2f}M" if v >= 1e6 else f"{sign}${v / 1e3:,.2f}K"


def pct(v, signed=False):
    return f"{v:+.2f}%" if signed else f"{v:.2f}%"


def new_page(title, subtitle, slicers):
    """16:9 canvas with header, slicer panel and mockup banner."""
    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor=CANVAS)
    fig.text(0.015, 0.955, title, fontsize=20, fontweight="bold", color=INK, va="center")
    fig.text(0.015, 0.918, subtitle, fontsize=11, color=INK_SECONDARY, va="center")
    # mockup tag (top right) + banner (bottom)
    fig.text(0.985, 0.955, "DESIGN MOCKUP", fontsize=11, fontweight="bold", color="white",
             ha="right", va="center",
             bbox=dict(boxstyle="round,pad=0.4", fc=LOSS, ec="none"))
    fig.text(0.5, 0.012, BANNER, fontsize=9, color=INK_SECONDARY, ha="center", style="italic")
    # slicer panel
    panel = fig.add_axes([0.875, 0.06, 0.115, 0.83])
    panel.set_axis_off()
    panel.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.02",
                                   fc=CARD_BG, ec=GRID, transform=panel.transAxes))
    panel.text(0.08, 0.96, "Slicers", fontsize=11, fontweight="bold", color=INK, va="top")
    y = 0.89
    for name, value in slicers:
        panel.text(0.08, y, name, fontsize=9, color=INK_SECONDARY, va="top")
        panel.text(0.08, y - 0.035, value, fontsize=10, color=INK, va="top", fontweight="bold",
                   bbox=dict(boxstyle="round,pad=0.3", fc="#F0EFEC", ec=GRID))
        y -= 0.11
    panel.text(0.08, 0.08, "↺ Reset filters", fontsize=9, color=PRIMARY, va="top")
    return fig


def card(fig, rect, label, value, sub=None, sub_color=None, value_color=INK):
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.04",
                                fc=CARD_BG, ec=GRID, transform=ax.transAxes))
    ax.text(0.07, 0.80, label, fontsize=10, color=INK_SECONDARY, va="center")
    ax.text(0.07, 0.45, value, fontsize=20, fontweight="bold", color=value_color, va="center")
    if sub:
        ax.text(0.07, 0.15, sub, fontsize=9.5, color=sub_color or INK_SECONDARY, va="center")


def panel_ax(fig, rect, title):
    ax = fig.add_axes(rect)
    ax.set_facecolor(CARD_BG)
    ax.set_title(title, fontsize=11, loc="left", color=INK, pad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(labelsize=8.5)
    return ax


def hbar(ax, labels, values, colors, fmt, xlim_pad=1.25):
    ax.barh(labels, values, color=colors, height=0.6)
    lo, hi = min(0, min(values)), max(0, max(values))
    span = (hi - lo) or 1
    for i, v in enumerate(values):
        # negative values are labelled just right of the zero line, in red
        x = v + span * 0.01 if v >= 0 else span * 0.01
        ax.text(x, i, fmt(v), va="center", ha="left", fontsize=8.5,
                color=INK_SECONDARY if v >= 0 else LOSS)
    ax.set_xlim(lo * 1.1 if lo < 0 else 0, hi * xlim_pad if hi > 0 else span * 0.3)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: ""))
    ax.tick_params(axis="x", length=0)


def table(fig, rect, title, frame, col_widths=None, red_negative_cols=()):
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.set_title(title, fontsize=11, loc="left", color=INK, pad=6)
    cell_text = frame.values.tolist()
    t = ax.table(cellText=cell_text, colLabels=list(frame.columns), loc="upper left",
                 cellLoc="right", colLoc="right", colWidths=col_widths)
    t.auto_set_font_size(False)
    t.set_fontsize(8.5)
    t.scale(1, 1.25)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor(GRID)
        if r == 0:
            cell.set_facecolor("#F0EFEC")
            cell.set_text_props(fontweight="bold", color=INK)
        else:
            cell.set_facecolor(CARD_BG)
            if frame.columns[c] in red_negative_cols and str(cell_text[r - 1][c]).startswith("-"):
                cell.set_text_props(color=LOSS)
        if c == 0:
            cell._loc = "left"
    return ax


def text_box(fig, rect, title, lines):
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.03",
                                fc="#FFF8F0", ec=BELOW, transform=ax.transAxes))
    ax.text(0.04, 0.9, title, fontsize=11, fontweight="bold", color=INK, va="top")
    width_chars = max(20, int(rect[2] * 16 * 100 / 7.2))   # approx. characters per line
    y = 0.76
    for line in lines:
        wrapped = textwrap.fill(line, width=width_chars, initial_indent="• ", subsequent_indent="   ")
        ax.text(0.04, y, wrapped, fontsize=9.3, color=INK, va="top", linespacing=1.35)
        y -= 0.09 * (wrapped.count("\n") + 1) + 0.06


def save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / name, facecolor=CANVAS)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_executive(df):
    y24, y23 = df[df["Year"] == 2024], df[df["Year"] == 2023]
    s24, s23, p24, p23 = y24["Sales"].sum(), y23["Sales"].sum(), y24["Profit"].sum(), y23["Profit"].sum()
    ys, yp = (s24 / s23 - 1) * 100, (p24 / p23 - 1) * 100
    m24, m23 = aggregate_margin(y24["Sales"], y24["Profit"]), aggregate_margin(y23["Sales"], y23["Profit"])

    fig = new_page("Executive Overview",
                   "Are we growing, and is the growth profitable?",
                   [("Year", "2024"), ("Region", "All"), ("Category", "All"), ("Segment", "All")])
    cards = [
        ("Sales", card_money(s24), f"YoY {pct(ys, True)}", PRIMARY, INK),
        ("Profit", card_money(p24), f"YoY {pct(yp, True)}", LOSS if yp < 0 else PRIMARY,
         LOSS if p24 < 0 else INK),
        ("Profit margin", pct(m24), f"Last year {pct(m23)}", INK_SECONDARY, INK),
        ("Orders", f"{y24['Order ID'].nunique():,}", None, None, INK),
        ("Units sold", f"{y24['Quantity'].sum():,}", None, None, INK),
        ("Profit growth − sales growth", f"{yp - ys:.2f} pp", "margin erosion", LOSS, LOSS),
    ]
    w = 0.135
    for i, (label, value, sub, sub_c, val_c) in enumerate(cards):
        card(fig, [0.015 + i * (w + 0.007), 0.75, w, 0.13], label, value, sub, sub_c, val_c)

    monthly = df.groupby("Year-Month")[["Sales", "Profit"]].sum()
    x = pd.PeriodIndex(monthly.index, freq="M").to_timestamp()
    for j, col in enumerate(["Sales", "Profit"]):
        ax = panel_ax(fig, [0.04 + j * 0.42, 0.45, 0.39, 0.23], f"Monthly {col.lower()}, 2021–2024 (not filtered by Year)")
        ax.plot(x, monthly[col], color=PRIMARY, linewidth=1.8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: money(v)))
        ax.set_ylim(min(0, monthly[col].min() * 1.2))

    reg = summarize_by(y24, "Region").sort_values("Sales")
    ax = panel_ax(fig, [0.06, 0.07, 0.30, 0.30], "Sales by region, 2024 (colour = margin vs company)")
    hbar(ax, reg.index, reg["Sales"], [margin_color(m, m24) for m in reg["Profit Margin %"]], money)

    cat = summarize_by(y24, "Category").sort_values("Profit")
    ax = panel_ax(fig, [0.45, 0.07, 0.22, 0.30], "Profit by category, 2024")
    hbar(ax, cat.index, cat["Profit"], [margin_color(m, m24) for m in cat["Profit Margin %"]], money, 1.45)

    central = y24[y24["Region"] == "Central"]
    ed24 = y24["Discount Amount"].sum() / y24["Gross Sales"].sum() * 100
    ed23 = y23["Discount Amount"].sum() / y23["Gross Sales"].sum() * 100
    text_box(fig, [0.70, 0.07, 0.165, 0.30], "Key messages", [
        f"Sales {pct(ys, True)} but profit {pct(yp, True)}; effective discount {ed23:.1f}% → {ed24:.1f}%.",
        f"Central made a loss ({money(central['Profit'].sum())}) on {money(central['Sales'].sum())} of sales.",
        f"Furniture lost {money(-cat.loc['Furniture', 'Profit'])}, driven by Tables.",
    ])
    save(fig, "01_executive_overview_mockup.png")


def page_regional(df):
    company = aggregate_margin(df["Sales"], df["Profit"])
    fig = new_page("Regional Performance",
                   "Which regions perform well, and which have profitability problems?",
                   [("Year", "(all years)"), ("Region", "All"), ("Category", "All"), ("Segment", "All")])
    reg = summarize_by(df, "Region")
    # exact (unrounded) margins for the "vs company" column, as the DAX measure would compute
    exact_margin = df.groupby("Region").apply(lambda g: aggregate_margin(g["Sales"], g["Profit"]),
                                              include_groups=False)
    yp = df.pivot_table(index="Region", columns="Year", values="Sales", aggfunc="sum")
    score = pd.DataFrame({
        "Region": reg.index,
        "Sales": [money(v) for v in reg["Sales"]],
        "Share": [pct(v) for v in reg["Sales Share %"]],
        "Profit": [money(v) for v in reg["Profit"]],
        "Margin": [pct(v) for v in reg["Profit Margin %"]],
        "vs Co. (pp)": [f"{exact_margin[r] - company:+.2f}" for r in reg.index],
        "Eff. discount": [pct(v) for v in reg["Effective Discount %"]],
        "Rank": range(1, len(reg) + 1),
    })
    table(fig, [0.015, 0.60, 0.50, 0.27], "Regional scorecard (YoY column appears when one year is selected)",
          score, red_negative_cols=("vs Co. (pp)",))

    order = reg.sort_values("Profit Margin %")
    ax = panel_ax(fig, [0.60, 0.62, 0.26, 0.25], f"Profit margin by region (line = company {company:.2f}%)")
    hbar(ax, order.index, order["Profit Margin %"],
         [margin_color(m, company) for m in order["Profit Margin %"]], pct)
    ax.axvline(company, color=INK_SECONDARY, linewidth=1, linestyle="-")

    order = reg.sort_values("Effective Discount %")
    ax = panel_ax(fig, [0.06, 0.08, 0.22, 0.42], "Share of list price given away as discount")
    hbar(ax, order.index, order["Effective Discount %"], PRIMARY, pct)

    ax = panel_ax(fig, [0.33, 0.08, 0.25, 0.42], "Yearly sales by region (not filtered by Year)")
    for region in yp.index:
        ax.plot(yp.columns, yp.loc[region], marker="o", linewidth=2, markersize=5,
                color=REGION_COLORS[region], label=region)
        ax.text(yp.columns[-1] + 0.08, yp.loc[region].iloc[-1], region, fontsize=8.5,
                va="center", color=INK_SECONDARY)
    ax.set_xticks(yp.columns)
    ax.set_xlim(yp.columns.min() - 0.2, yp.columns.max() + 0.6)
    ax.set_ylim(0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: money(v)))

    st = summarize_by(df, "State").sort_values("Profit Margin %")
    ax = panel_ax(fig, [0.66, 0.08, 0.20, 0.45], "Margin by state (Power BI: filled map)")
    lim = np.abs(st["Profit Margin %"]).max()
    colors = PROFIT_CMAP((st["Profit Margin %"] + lim) / (2 * lim))
    ax.barh(st.index, st["Profit Margin %"], color=colors, height=0.7)
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.tick_params(axis="y", labelsize=7)
    ax.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.grid(axis="y", visible=False)
    save(fig, "02_regional_performance_mockup.png")


def page_product(df):
    company = aggregate_margin(df["Sales"], df["Profit"])
    fig = new_page("Product Performance", "Which products are destroying profit?",
                   [("Year", "(all years)"), ("Region", "All"), ("Category", "All"), ("Segment", "All")])
    cat = summarize_by(df, "Category")
    table(fig, [0.015, 0.73, 0.30, 0.14], "Category summary", pd.DataFrame({
        "Category": cat.index, "Sales": [money(v) for v in cat["Sales"]],
        "Profit": [money(v) for v in cat["Profit"]], "Margin": [pct(v) for v in cat["Profit Margin %"]]}),
        red_negative_cols=("Profit", "Margin"))

    sub = summarize_by(df, "Sub-Category").sort_values("Profit", ascending=False)
    ax = panel_ax(fig, [0.08, 0.06, 0.22, 0.58], "Profit by sub-category (red = loss)")
    hbar(ax, sub.index, sub["Profit"], [margin_color(m, company) for m in sub["Profit Margin %"]], money, 1.4)
    ax.tick_params(axis="y", labelsize=8)

    prod = summarize_by(df, "Product Name")
    flagged = high_sales_low_profit(df)
    ax = panel_ax(fig, [0.37, 0.52, 0.48, 0.35], "Product sales vs profit (red = top-25% sales, margin < 5%)")
    hit = prod.index.isin(flagged.index)
    ax.scatter(prod.loc[~hit, "Sales"], prod.loc[~hit, "Profit"], s=16, color=MUTED)
    ax.scatter(prod.loc[hit, "Sales"], prod.loc[hit, "Profit"], s=30, color=LOSS, edgecolor="white")
    ax.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: money(v)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: money(v)))

    t = flagged.reset_index()
    table(fig, [0.37, 0.06, 0.27, 0.38], f"High sales, low margin: action list ({len(t)} products)", pd.DataFrame({
        "Product": t["Product Name"], "Sales": [money(v) for v in t["Sales"]],
        "Profit": [money(v) for v in t["Profit"]], "Margin": [pct(v) for v in t["Profit Margin %"]]}),
        col_widths=[0.46, 0.18, 0.18, 0.18], red_negative_cols=("Profit", "Margin"))

    bottom = top_n(df, "Product Name", metric="Profit", n=10, ascending=True).reset_index()
    table(fig, [0.66, 0.06, 0.20, 0.38], "10 biggest loss-makers", pd.DataFrame({
        "Product": bottom["Product Name"], "Profit": [money(v) for v in bottom["Profit"]]}),
        col_widths=[0.66, 0.34], red_negative_cols=("Profit",))
    save(fig, "03_product_performance_mockup.png")


def page_customer(df):
    fig = new_page("Customer Performance", "Which customers and segments matter, and are they profitable?",
                   [("Year", "(all years)"), ("Region", "All"), ("Category", "All"), ("Segment", "All")])
    n_cust, orders = df["Customer ID"].nunique(), df["Order ID"].nunique()
    for i, (label, value) in enumerate([
            ("Active customers", f"{n_cust:,}"),
            ("Sales per customer", f"${df['Sales'].sum() / n_cust:,.2f}"),
            ("Average order value", f"${df['Sales'].sum() / orders:,.2f}")]):
        card(fig, [0.015 + i * 0.145, 0.75, 0.135, 0.13], label, value)

    seg = summarize_by(df, "Segment").sort_values("Sales")
    ax = panel_ax(fig, [0.53, 0.75, 0.15, 0.12], "Sales by segment")
    hbar(ax, seg.index, seg["Sales"], PRIMARY, money, 1.5)
    ax = panel_ax(fig, [0.75, 0.75, 0.11, 0.12], "Margin by segment")
    hbar(ax, seg.index, seg["Profit Margin %"], PRIMARY, pct, 1.6)
    ax.set_yticklabels([])

    top = top_n(df, "Customer Name", n=10).sort_values("Sales")
    ax = panel_ax(fig, [0.10, 0.10, 0.24, 0.55], "Top 10 customers by sales")
    hbar(ax, top.index, top["Sales"], PRIMARY, money, 1.3)

    cust = df.groupby(["Customer Name", "Segment"]).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    cust["Margin"] = cust["Profit"] / cust["Sales"] * 100
    ax = panel_ax(fig, [0.40, 0.10, 0.45, 0.55], "Customers: size vs profitability (one dot per customer)")
    for seg_name, color in zip(["Consumer", "Corporate", "Home Office"], [PRIMARY, "#EB6834", "#1BAF7A"]):
        c = cust[cust["Segment"] == seg_name]
        ax.scatter(c["Sales"], c["Margin"], s=14, color=color, alpha=0.75, label=seg_name)
    ax.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax.set_ylim(max(cust["Margin"].min(), -60), cust["Margin"].max() * 1.05)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: money(v)))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlabel("Total sales", fontsize=9)
    ax.set_ylabel("Profit margin", fontsize=9)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)
    save(fig, "04_customer_performance_mockup.png")


def page_profitability(df):
    company = aggregate_margin(df["Sales"], df["Profit"])
    fig = new_page("Profitability & Discount", "Are discounts causing margin problems, and what should management investigate?",
                   [("Year", "(all years)"), ("Region", "All"), ("Category", "All"), ("Segment", "All")])
    deep = df[df["Discount"] >= 0.3]
    over20 = df[df["Discount"] > 0.2]
    uplift = (over20["Gross Sales"] * (over20["Discount"] - 0.2)).sum()
    card(fig, [0.015, 0.75, 0.19, 0.13], "Profit on lines with ≥30% discount", card_money(deep["Profit"].sum()),
         f"{len(deep):,} order lines", value_color=LOSS)
    card(fig, [0.215, 0.75, 0.21, 0.13], "What-if: cap discounts at 20%", "+" + card_money(uplift),
         "Upper bound: assumes unchanged volume")
    card(fig, [0.435, 0.75, 0.15, 0.13], "Order lines that lose money", pct((df["Profit"] < 0).mean() * 100))

    d = discount_impact(df)
    ax = panel_ax(fig, [0.04, 0.08, 0.30, 0.56], "Profit margin at each discount level")
    labels = [f"{x:.0%}" for x in d.index]
    ax.bar(labels, d["Profit Margin %"], color=[margin_color(m, company) for m in d["Profit Margin %"]], width=0.65)
    for i, v in enumerate(d["Profit Margin %"]):
        ax.text(i, v, f"{v:.0f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=8, color=INK_SECONDARY)
    ax.axhline(0, color=INK_SECONDARY, linewidth=0.8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_ylim(d["Profit Margin %"].min() * 1.15, d["Profit Margin %"].max() * 2)
    ax.grid(axis="x", visible=False)

    m = region_subcategory_profit(df) / 1000
    m = m.loc[m.sum(axis=1).sort_values().index]
    ax = panel_ax(fig, [0.43, 0.08, 0.20, 0.56], "Profit ($K) by sub-category and region")
    lim = np.abs(m.values).max()
    ax.imshow(m.values, cmap=PROFIT_CMAP, vmin=-lim, vmax=lim, aspect="auto")
    ax.set_xticks(range(m.shape[1]), m.columns, fontsize=8.5)
    ax.set_yticks(range(m.shape[0]), m.index, fontsize=8)
    for (r, c), v in np.ndenumerate(m.values):
        ax.text(c, r, f"{v:.1f}", ha="center", va="center", fontsize=7.5,
                color="white" if abs(v) > lim * 0.55 else INK)
    ax.grid(False)

    loss = top_n(df, "Product Name", metric="Profit", n=10, ascending=True).reset_index()
    eff = summarize_by(df, "Product Name")["Effective Discount %"]
    table(fig, [0.655, 0.40, 0.21, 0.30], "Loss-making products (worst 10)", pd.DataFrame({
        "Product": loss["Product Name"], "Profit": [money(v) for v in loss["Profit"]],
        "Eff. disc.": [pct(eff[p]) for p in loss["Product Name"]]}),
        col_widths=[0.62, 0.20, 0.18], red_negative_cols=("Profit",))

    central = df[df["Region"] == "Central"]
    others = df[df["Region"] != "Central"]
    text_box(fig, [0.66, 0.06, 0.20, 0.28], "Investigate next", [
        f"Central: {(central['Discount'] >= 0.3).mean():.0%} of lines at 30%+ discount vs "
        f"{(others['Discount'] >= 0.3).mean():.0%} elsewhere.",
        "Tables lose money even at 10–20% discounts: review price & supplier cost.",
        "South: sales −12%/yr with ~10% margin. Investigate lost customers.",
    ])
    save(fig, "05_profitability_discount_mockup.png")


def page_region_detail(df, region="Central"):
    r = df[df["Region"] == region]
    fig = new_page(f"Region Detail: {region}  (hidden drill-through page)",
                   "Opened by right-clicking a region → Drill through → Region Detail",
                   [("Drill-through", region), ("Year", "(all years)")])
    by_city = r.groupby(["State", "City"]).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
                                               Gross=("Gross Sales", "sum"), Disc=("Discount Amount", "sum"))
    by_city = by_city.sort_values("Sales", ascending=False).reset_index()
    rows = pd.DataFrame({
        "State": by_city["State"], "City": by_city["City"],
        "Sales": [money(v) for v in by_city["Sales"]], "Profit": [money(v) for v in by_city["Profit"]],
        "Margin": [pct(p / s * 100) for p, s in zip(by_city["Profit"], by_city["Sales"])],
        "Eff. disc.": [pct(d / g * 100) for d, g in zip(by_city["Disc"], by_city["Gross"])],
    })
    total = pd.DataFrame([{"State": "Total", "City": "", "Sales": money(r["Sales"].sum()),
                           "Profit": money(r["Profit"].sum()),
                           "Margin": pct(aggregate_margin(r["Sales"], r["Profit"])),
                           "Eff. disc.": pct(r["Discount Amount"].sum() / r["Gross Sales"].sum() * 100)}])
    table(fig, [0.015, 0.36, 0.50, 0.51], f"{region} by state and city", pd.concat([rows, total]),
          red_negative_cols=("Profit", "Margin"))
    worst = top_n(r, "Product Name", metric="Profit", n=10, ascending=True).reset_index()
    table(fig, [0.55, 0.36, 0.31, 0.51], f"Biggest loss-making products in {region}", pd.DataFrame({
        "Product": worst["Product Name"], "Profit": [money(v) for v in worst["Profit"]]}),
        col_widths=[0.7, 0.3], red_negative_cols=("Profit",))
    city = by_city.assign(Margin=by_city["Profit"] / by_city["Sales"] * 100,
                          Label=by_city["City"] + ", " + by_city["State"]).sort_values("Margin")
    ax = panel_ax(fig, [0.12, 0.07, 0.40, 0.36], f"Profit margin by city in {region} (red = loss, orange = below company margin)")
    company = aggregate_margin(df["Sales"], df["Profit"])
    hbar(ax, city["Label"], city["Margin"], [margin_color(m, company) for m in city["Margin"]], pct, 1.3)
    ax.tick_params(axis="y", labelsize=7.5)
    save(fig, "06_region_detail_central_mockup.png")


def main():
    set_chart_style()
    plt.rcParams["text.parse_math"] = False   # "$" in money values must not start math mode
    df = pd.read_csv(CLEAN_FILE, parse_dates=["Order Date", "Ship Date"])
    page_executive(df)
    page_regional(df)
    page_product(df)
    page_customer(df)
    page_profitability(df)
    page_region_detail(df)
    print(f"Mockups written to {OUT_DIR}")


if __name__ == "__main__":
    main()
