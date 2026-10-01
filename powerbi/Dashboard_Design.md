# Power BI Dashboard Design

> **Status: specification only, Power BI Desktop work required.** This repository contains no `.pbix` file and no dashboard screenshots. Power BI Desktop runs only on Windows. This document is the design you build from; the click-by-click instructions are in [POWER_BI_MASTER_GUIDE.md](POWER_BI_MASTER_GUIDE.md). Every value quoted here was computed in Python and confirmed in MySQL.

**Visual preview:** [mockups/](mockups/) has all 6 pages rendered in Python from the real data. They are design mockups, not Power BI screenshots.

**Builds on:** [Data_Model.md](Data_Model.md) (tables & relationships) · [DAX_Measures.md](DAX_Measures.md) (formulas) · [DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md) (expected values)

---

## 1. What management must be able to answer

The report is designed backwards from these questions. Each one is answered on a specific page:

| # | Management question | Page | The visual that answers it | Answer in this data |
|---|---|---|---|---|
| 1 | How are sales performing? | 1 Executive | Sales card + YoY, monthly trend | 2024 $1.19M, **+6.7%** |
| 2 | How is profit performing? | 1 Executive | Profit card + YoY, Growth Gap card | 2024 $110K, **−6.6%**; margin 9.2% |
| 3 | Which regions are performing well? | 2 Regional | Region scorecard table | West (size, growth), East (margin 13.2%) |
| 4 | Which regions have profitability problems? | 2 Regional | Margin vs company bars, discount by region | **Central 3.3%** (−0.4% in 2024) |
| 5 | Which products are destroying profit? | 3 Product | Profit by sub-category, high-sales/low-margin table | **Tables −$91.5K, Bookcases −$30.4K** |
| 6 | Are discounts causing margin problems? | 5 Profitability | Margin by discount level, deep-discount card | Every level ≥ 30% loses money: **−$249K** |
| 7 | Which customer segments matter? | 4 Customer | Segment bars, customer scatter | Consumer 54% of sales; Corporate best margin |
| 8 | What changed over time? | 1 Executive, 2 Regional | Monthly trend, yearly sales by region | West/East growing, South −12%/yr, Central profit → loss |
| 9 | What should management investigate? | 5 Profitability | "Investigate next" text box + matrix | Central discount approvals; Tables pricing; South volume |

**Design rules:**
1. **Margin is always next to sales.** Sales alone hides this project's main finding.
2. **One page = one audience question.** Five pages, no more.
3. **Top-left is read first:** KPI cards in the top row, the main chart below, detail at the bottom.
4. **Colour has a job.** Blue = normal; orange = below company margin; **red = loss only**. A region keeps the same colour everywhere (Central blue `#2A78D6`, East orange `#EB6834`, South aqua `#1BAF7A`, West yellow `#EDA100`), used only where regions are separate series.
5. **No dual axes** and **no pies** for close values.
6. **Every title states the question or the answer**, e.g. "Central keeps 3¢ of every $1 sold".

**Canvas:** 16:9 (1280 × 720). Background `#FCFCFB`, text `#0B0B0B`/`#52514E`, gridlines `#E1E0D9`.

## 2. Global elements (on every page)

| Element | Setting | Why |
|---|---|---|
| **Slicer: Year** | `DimDate[Year]`, *Tile*, single select **Off** (Ctrl + click for several years), default **2024** via the Default bookmark | Management looks at the latest year first; clearing the slicer shows all four years |
| **Slicer: Region** | `DimGeography[Region]`, dropdown, multi-select | Regional managers filter to their region |
| **Slicer: Category** | `DimProduct[Category]`, dropdown | Product questions |
| **Slicer: Segment** | `DimCustomer[Segment]`, dropdown | Customer questions |
| **Sync slicers** | *View → Sync slicers*: all four synced across all pages | A filter chosen on page 1 still applies on page 3 |
| **Page navigator** | *Insert → Buttons → Navigator → Page navigator* | Easy movement between pages |
| **Reset button** | Bookmark "Default" (Year = 2024, others cleared) + button | One click back to the default view |
| **Data note** | Small text, bottom right: "Synthetic RetailCo data, 2021–2024. Values: Sales after discount." | Honesty and context |

> **How the Year slicer behaves:** one year selected → every measure shows that year, and YoY cards show growth vs the previous year. Slicer **cleared** (eraser icon) → all four years; YoY cards are BLANK by design, because `YoY Sales Growth %` needs exactly one year (DAX_Measures Part 4). The slicer is synced, so whatever you choose applies on every page. **Every validation table below states the slicer state it assumes.**

---

## Page 1 · Executive Overview
**Audience:** CEO, Finance Manager. **Objective:** tell, in 10 seconds, whether the business is growing *profitably*.
**Business question:** *Are we growing, and is the growth profitable?*

```
┌─────────┬─────────┬─────────┬─────────┬─────────┬──────────┬────────────┐
│ Sales   │ Profit  │ Margin  │ Orders  │ Qty     │ Growth   │  Slicers   │
│ ▲ YoY   │ ▼ YoY   │ vs PY   │         │         │ Gap (pp) │            │
├─────────┴─────────┴─────────┴─────────┴─────────┴──────────┤            │
│ Monthly sales & profit trend (two small line charts)       │            │
├──────────────────────────────┬─────────────────────────────┼────────────┤
│ Sales & margin by region     │ Profit by category          │ Key        │
│ (bar, colour = Margin Color) │ (bar, red if < 0)           │ messages   │
└──────────────────────────────┴─────────────────────────────┴────────────┘
```

| Visual | Type | Fields | Why this visual |
|---|---|---|---|
| Sales card | Card (new), reference label | `[Total Sales]`; reference label `[YoY Sales Growth %]` | A headline number is best shown as a number |
| Profit card | Card (new), reference label | `[Total Profit]`; `[YoY Profit Growth %]` | Puts profit growth right next to sales growth |
| Margin card | Card (new), reference label | `[Profit Margin %]`; reference label `[Profit Margin PY]` | Efficiency, not size; shows the drop from last year |
| Orders / Quantity | Cards | `[Total Orders]`, `[Total Quantity]` | Volume context |
| Growth Gap | Card, conditional colour red if < 0 | `[Growth Gap (pp)]` | The early-warning number: profit growing slower than sales |
| Monthly trend | 2 line charts stacked (not dual axis) | X `DimDate[Year-Month]` (Year slicer **not** applied: *Edit interactions → None*), Y `[Total Sales]`; second chart `[Total Profit]` | Seasonality and trend across all 4 years |
| Sales & margin by region | Clustered bar | Y `DimGeography[Region]`, X `[Total Sales]`, bar colour `[Margin Color]`, tooltip `[Profit Margin %]` | Size *and* health in one bar |
| Profit by category | Clustered bar | `DimProduct[Category]`, `[Total Profit]`, colour `[Margin Color]` | Furniture's loss stands out |
| Key messages | Text box | 3 bullet points written by the analyst | Management reads conclusions, not just charts |

**Interactions:** clicking a region bar filters the cards and the category chart. The monthly trend ignores the Year slicer so the 4-year context is always visible.
**Expected insight:** sales up, profit down; the region chart shows Central orange despite decent sales.

| Validation (Year = 2024) | Expected |
|---|---|
| Sales / YoY | 1,192,590.88 / +6.69% |
| Profit / YoY | 110,241.76 / −6.63% |
| Margin / Margin PY | 9.24% / 10.56% |
| Orders / Quantity | 1,393 / 15,341 |
| Growth Gap | −13.32 pp |
| Category profit | Technology 66,402.91 · Office Supplies 49,894.89 · Furniture **−6,056.04** |

**Key-messages text (2024 view):**
* Sales grew 6.7% but profit fell 6.6%. Growth came with deeper discounts (effective discount 15.6% → 16.2%).
* Central made a loss in 2024 (−$744) on $204K of sales.
* Furniture lost $6.1K in 2024, driven by Tables.

---

## Page 2 · Regional Performance
**Audience:** Sales Manager, Regional Managers. **Objective:** rank regions on size, growth *and* profitability, and show *why* a region is weak.
**Business questions:** *Which regions are performing well? Which have profitability problems?*

| Visual | Type | Fields | Why |
|---|---|---|---|
| Region scorecard | Table | `DimGeography[Region]`, `[Total Sales]`, `[Sales Share %]`, `[YoY Sales Growth %]`, `[Total Profit]`, `[Profit Margin %]`, `[Margin vs Company]`, `[Effective Discount %]`, `[Region Rank]` | Every regional KPI side by side. Conditional formatting: `Margin vs Company` red background when < 0; `YoY` red font when < 0 |
| Margin by region | Bar + constant line | `[Profit Margin %]`; *Analytics → Constant line* bound to `[Company Margin]` (fx) | Above/below company at a glance |
| Effective discount by region | Bar | `[Effective Discount %]` | Puts the likely cause next to the margin chart |
| Yearly sales by region | Line chart | X `DimDate[Year]`, Y `[Total Sales]`, Legend `DimGeography[Region]`; Year slicer interaction **None** | Growth vs decline over 4 years |
| Map | Filled map | Location `DimGeography[State Location]` (see step-by-step §21), colour saturation `[Profit Margin %]`, diverging, centre 0 | The question is *where*. Uses margin, not sales, so big states don't automatically look "good" |

**Slicers:** global. **Interactions:** selecting a region in the scorecard filters the map and the discount bar.
**Drill-through:** hidden page **Region Detail** (drill-through field `DimGeography[Region]`): state/city table with Sales, Profit, Margin, Effective Discount, plus the top 10 loss-making products. Right-click a region → *Drill through → Region Detail*.
**Expected insight:** Central has the highest discount and the lowest margin; South is shrinking but its margin is healthy.

| Validation ("All years" = Year slicer cleared) | Expected |
|---|---|
| All years: margin | East 13.23% · West 12.27% · South 10.00% · Central 3.28% |
| All years: effective discount | Central 21.51% · South 15.01% · West 13.47% · East 13.46% |
| All years: Margin vs Company | Central −7.01 · South −0.30 · West +1.97 · East +2.94 |
| Year = 2024: YoY sales | East +25.76% · West +12.07% · Central −12.05% · South −12.18% |
| Year = 2024: margin | East 12.02% · West 11.60% · South 8.36% · Central **−0.37%** |
| Year = 2024: effective discount | Central 23.68% · South 16.45% · East 14.47% · West 13.65% |

---

## Page 3 · Product Performance
**Audience:** Category Manager, Procurement. **Objective:** find products that look successful but destroy profit.
**Business question:** *Which products are destroying profit?*

| Visual | Type | Fields | Why |
|---|---|---|---|
| Category cards | 3 cards (or multi-row card) | per category: `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]` | Quick comparison |
| Profit by sub-category | Bar, sorted ascending | `DimProduct[Sub-Category]`, `[Total Profit]`, colour `[Margin Color]` | Loss-makers sit at the top in red |
| Sales vs profit scatter | Scatter | Values `DimProduct[Product Name]`, X `[Total Sales]`, Y `[Total Profit]`, Legend → none; colour via *fx* rule on `[High Sales Low Margin]` = 1 → red | Bottom-right = high sales, negative profit |
| High-sales / low-margin table | Table, visual filter `[High Sales Low Margin]` is 1 | Product Name, Sub-Category, Sales, Profit, Margin, `[Effective Discount %]` | The action list (8 products) |
| Top 10 / Bottom 10 | Two tables, *Filters → Product Name → Top N* = 10 by `[Total Sales]` / bottom 10 by `[Total Profit]` | Ranked lists |

**Interactions:** clicking a sub-category bar filters the scatter and the tables.
**Expected insight:** Tables and Bookcases lose money in every region; the best-selling product (Orbit Smartphone L502, $143K) earns only 4.8%.

| Validation (Year slicer cleared = all years) | Expected |
|---|---|
| Category profit | Technology 252,948.63 · Office Supplies 200,916.89 · Furniture −1,797.48 |
| Sub-category profit | Tables −91,521.11 · Bookcases −30,446.26 · Supplies −1,745.06 · Phones 94,432.52 (highest) |
| High-sales/low-margin rows | 8 |
| Bottom product | Round Table M702: −26,412.30 |

---

## Page 4 · Customer Performance
**Audience:** Sales Manager, Account Managers. **Objective:** show who matters most and whether they are profitable.
**Business question:** *Which customer segments and customers matter?*

| Visual | Type | Fields | Why |
|---|---|---|---|
| Customer cards | Cards | `[Customers]`, `[Average Order Value]`, `[Sales per Customer]` | Context |
| Segment performance | 2 small bars (no dual axis) | `DimCustomer[Segment]` × `[Total Sales]`; × `[Profit Margin %]` | Size vs efficiency per segment |
| Top 10 customers | Bar, Top N 10 by `[Total Sales]` | `DimCustomer[Customer Name]` | Ranking |
| Customer profitability scatter | Scatter | Values `DimCustomer[Customer Name]`, X `[Total Sales]`, Y `[Profit Margin %]`, Legend `DimCustomer[Segment]` | Shows the spread of customers, and big customers with thin margins (bottom-right). Responds to all slicers |
| Customer table | Table | Name, Segment, Sales, Profit, Margin, `[Effective Discount %]`, `[Total Orders]` | Detail for account managers |

**Expected insight:** Consumer brings 54% of sales; segment margins are close (9–11%), so segment is not the main profit lever. Some large customers buy almost only at deep discounts (e.g. $41.7K sales at 1.1% margin).

| Validation (Year slicer cleared = all years, unless stated) | Expected |
|---|---|
| Customers / Sales per Customer | 741 (Consumer 406 · Corporate 189 · Home Office 146) / 5,926.01 |
| Segment sales | Consumer 2,379,132.35 · Corporate 1,176,807.57 · Home Office 835,236.08 |
| Segment margin | Corporate 11.12% · Consumer 10.29% · Home Office 9.15% |
| Top customer | Grace Diaz: 69,516.61 |
| Year = 2024: customers | 544 |

---

## Page 5 · Profitability & Discount
**Audience:** Finance Manager, CEO. **Objective:** explain *where* and *why* profit leaks, and what to investigate next.
**Business questions:** *Are discounts causing margin problems? What should management investigate?*

| Visual | Type | Fields | Why |
|---|---|---|---|
| Deep-discount loss | Card | `[Deep Discount Profit]` | Size of the problem |
| What-if card | Card, subtitle "Upper bound: assumes the same quantity would still sell" | `[Max Uplift (Cap 20%)]` | Sizing, honestly labelled |
| Loss lines | Card | `[Loss Line %]` | How widespread losses are |
| Margin by discount level | Column chart | X `FactSales[Discount]` (*Format → X axis → Type: Categorical*), Y `[Profit Margin %]`, colour `[Margin Color]` | Shows the break-even threshold between 20% and 30% |
| Profitability matrix | Matrix | Rows `DimProduct[Sub-Category]`, Columns `DimGeography[Region]`, Values `[Total Profit]`; *Cell elements → Background colour → Gradient, diverging: red (min) – white (0) – blue (max)* | Locates losses: Tables in every region, Central weakest |
| Loss-making products | Table, visual filter `[Total Profit]` < 0 | Product Name, Sub-Category, Profit, `[Effective Discount %]` | Action list |
| Investigate next | Text box | see below | Turns the page into a decision |

**Investigate-next text:**
1. **Central discount approvals:** 28% of Central's lines carry 30%+ discounts, against about 13% elsewhere. Who approves them?
2. **Tables pricing:** Tables lose money even at 10–20% discounts. Review list price and supplier cost.
3. **South volume:** sales fell 12%/yr while margin stayed ~10%. Investigate lost customers, not prices.

**Expected insight:** margin falls from 24.9% at no discount to 5.8% at 20%, and turns negative at every level from 30% upward.

| Validation ("All years" = Year slicer cleared) | Expected |
|---|---|
| All years: Deep Discount Profit | −249,356.36 (Year = 2024: −81,467.69) |
| All years: Max Uplift | 264,266.66 (Year = 2024: 83,691.16) |
| All years: Loss Line % | 16.64% (Year = 2024: 16.95%) |
| Margin at discount 0 / 0.2 / 0.3 / 0.8 | 24.86% / 5.78% / −7.72% / −319.52% |
| Matrix: Central × Tables | −32,951 (largest loss cell) |

---

## Final dashboard validation (before screenshots)

1. All rows of [DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md) ticked.
2. Every page's validation table above matches.
3. Clear all slicers and check that the Year slicer returns to 2024 via the Reset button.
4. Select Region = Central: check that every page updates and nothing shows an error.
5. Ask someone unfamiliar with the project: "Which region needs attention, and why?" They should answer within 60 seconds from pages 1–2.

## Performance (if it ever gets slow)

* *View → Performance analyzer → Start recording → Refresh visuals* to find the slow visual.
* Keep the star schema with single-direction relationships; remove unused columns in Power Query.
* Prefer measures over calculated columns; avoid `FILTER` over the whole fact table where a boolean `CALCULATE` filter works.
* Roughly 8–10 visuals per page; no high-cardinality fields (Order ID) on axes.
* For large data: aggregation tables, incremental refresh, or DirectQuery for detail tables only.

## Deployment (in a real company; not part of this project)

1. Publish to a Power BI Service workspace.
2. Connect to the company database through a gateway; schedule a daily refresh.
3. **Row-level security**: role `RegionalManager` with a DAX filter on `DimGeography[Region]`, driven by `USERPRINCIPALNAME()` and a user-to-region mapping table.
4. Distribute as an App; set alerts on the margin card.
5. Version the report in Git using the **PBIP** project format (text files, diff-friendly) rather than only the binary `.pbix`.
