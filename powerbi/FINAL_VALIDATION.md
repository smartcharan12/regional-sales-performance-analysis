# Final Power BI Validation Procedure

**Purpose:** prove the dashboard is correct before you show it to anyone, put screenshots on GitHub, or describe it as "validated" in an interview.

**Where the expected values come from:** Python, computed from `data/processed/sales_cleaned.csv` (notebook 04 and the pipeline), with the headline figures confirmed in MySQL 8 (`sql/*.sql`, identical to the cent), and pinned by `tests/test_pipeline.py`. **None of the *Actual* values have been filled in.** They can only come from your Power BI Desktop file.

**How to use:** work through Levels 1 → 4 in order. Write each *Actual* value into the final table, and mark *Pass* only if it matches *Expected* (to 2 decimals). If anything fails, stop and fix it ([POWER_BI_TROUBLESHOOTING.md](POWER_BI_TROUBLESHOOTING.md)) before moving to the next level. Errors upstream cause errors downstream.

---

## LEVEL 1: Data (did the right rows arrive?)

**Where:** **Table view** ▦ → click each table → row count at the bottom-left.

| Check | Expected |
|---|---|
| FactSales rows | 11,461 |
| DimDate rows | 1,461 |
| DimCustomer rows | 741 |
| DimProduct rows | 174 |
| DimGeography rows | 36 |
| FactSales: blank `Ship Date` values | 6 (*Transform data* → column profile, or filter the column on "(blank)") |
| No error cells in any query | 0 errors (*Transform data → View → Column quality*: "Error 0%") |

## LEVEL 2: Model (are the tables connected correctly?)

**Where:** **Model view** ⧉ and *Home → Manage relationships*.

| Check | Expected |
|---|---|
| Number of relationships | Exactly 4, all active |
| `DimDate[Date]` → `FactSales[Order Date]` | 1:\*, Single |
| `DimCustomer[Customer ID]` → `FactSales[Customer ID]` | 1:\*, Single |
| `DimProduct[Product ID]` → `FactSales[Product ID]` | 1:\*, Single |
| `DimGeography[GeoKey]` → `FactSales[GeoKey]` | 1:\*, Single |
| `DimDate` marked as date table on `Date` | Yes |
| `DimDate[Month]` sorted by `Month Number` | Yes (charts show Jan…Dec) |
| **Functional test:** Validation page, table `DimGeography[Region]` + `[Total Sales]` | West 1,512,745.30 · East 1,195,924.92 · Central 892,318.30 · South 790,187.48 |
| **Functional test:** table `DimDate[Year]` + `[Total Sales]` | 2021 1,045,575.54 · 2022 1,035,179.93 · 2023 1,117,829.65 · 2024 1,192,590.88 |

The functional tests prove that filters really flow from each dimension into the fact table.

## LEVEL 3: DAX (does every measure return the right number?)

**Where:** the hidden **Validation** page (no slicers).
Complete every row of **[DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md)**: 31 measures. The key ones are repeated in the final table below.

Also check:
- [ ] No measure shows a yellow ⚠ warning in the *Data* pane
- [ ] With no filters, the YoY cards are **blank** (correct by design)

## LEVEL 4: Dashboard (do the visuals show the right story?)

**Where:** each report page, with the slicer state stated. For a side-by-side visual check, compare each page with its design mockup in [mockups/](mockups/) (same numbers; rendered in Python, not Power BI).

| Page | Slicer state | Check | Expected |
|---|---|---|---|
| Executive Overview | Year = 2024 | Sales card / YoY | 1,192,590.88 (1.19M) / 6.69% |
| Executive Overview | Year = 2024 | Profit card / YoY | 110,241.76 / −6.63% (red) |
| Executive Overview | Year = 2024 | Margin card / reference | 9.24% / 10.56% |
| Executive Overview | Year = 2024 | Growth Gap card | −13.32 |
| Executive Overview | Year = 2024 | Furniture bar (profit by category) | −6,056.04, red |
| Executive Overview | Year = 2024 | Trend charts still show 2021–2024 | Yes (interaction = None) |
| Regional Performance | Year cleared | Central margin / effective discount | 3.28% / 21.51% |
| Regional Performance | Year cleared | Margin vs Company (Central) | −7.01 |
| Regional Performance | Year = 2024 | South YoY sales | −12.18% |
| Regional Performance | Year cleared | Drill-through Central → Region Detail total margin | 3.28% |
| Product Performance | Year cleared | Tables profit bar | −91,521.11, red |
| Product Performance | Year cleared | High-sales/low-margin table rows | 8 |
| Customer Performance | Year cleared | Customers / Sales per Customer | 741 / 5,926.01 |
| Customer Performance | Year cleared | Top customer | Grace Diaz, 69,516.61 |
| Profitability & Discount | Year cleared | Deep Discount Profit / Max Uplift | −249,356.36 / 264,266.66 |
| Profitability & Discount | Year cleared | Margin at discount 0.3 | −7.72% |
| Profitability & Discount | Year cleared | Matrix cell Central × Tables | −32,951 (deepest red) |
| All pages | Region = Central | Every visual updates; no errors | Yes |
| All pages | – | Reset button returns to Year = 2024, other slicers cleared | Yes |

**Usability check:** ask someone who hasn't seen the project, "Which region needs attention, and why?" Pass if they answer from pages 1–2 within about 60 seconds ("Central: low margin, heavy discounting").

---

## Final validation table

Fill in *Actual* from Power BI Desktop. **Do not tick Pass/Fail until you've looked at the value.**

| # | Level | Validation | Expected | Actual | Pass/Fail |
|---|---|---|---|---|---|
| 1 | Data | FactSales rows | 11,461 | | |
| 2 | Data | DimDate rows | 1,461 | | |
| 3 | Data | DimCustomer rows | 741 | | |
| 4 | Data | DimProduct rows | 174 | | |
| 5 | Data | DimGeography rows | 36 | | |
| 6 | Model | Relationships (all 1:\*, single, active) | 4 | | |
| 7 | Model | DimDate marked as date table | Yes | | |
| 8 | Model | Total Sales by Region: Central | 892,318.30 | | |
| 9 | DAX | Total Sales (no filter) | 4,391,176.00 | | |
| 10 | DAX | Total Profit (no filter) | 452,068.04 | | |
| 11 | DAX | Profit Margin % (no filter) | 10.29% | | |
| 12 | DAX | Total Orders (no filter) | 5,190 | | |
| 13 | DAX | Total Quantity (no filter) | 56,703 | | |
| 14 | DAX | Average Order Value (no filter) | 846.08 | | |
| 15 | DAX | Effective Discount % (no filter) | 15.50% | | |
| 16 | DAX | Sales PY (Year = 2024) | 1,117,829.65 | | |
| 17 | DAX | YoY Sales Growth % (Year = 2024) | 6.69% | | |
| 18 | DAX | YoY Profit Growth % (Year = 2024) | −6.63% | | |
| 19 | DAX | Profit Margin % (Region = Central) | 3.28% | | |
| 20 | DAX | Deep Discount Profit (no filter) | −249,356.36 | | |
| 21 | DAX | Max Uplift (Cap 20%) (no filter) | 264,266.66 | | |
| 22 | DAX | All 31 rows of DAX_VALIDATION_CHECKLIST ☑ | 31 / 31 | | |
| 23 | Dashboard | Executive cards (Year = 2024) match Level 4 | Yes | | |
| 24 | Dashboard | Regional page values match Level 4 | Yes | | |
| 25 | Dashboard | Product page: action list rows | 8 | | |
| 26 | Dashboard | Customer page: customers | 741 | | |
| 27 | Dashboard | Profitability page: matrix Central × Tables | −32,951 | | |
| 28 | Dashboard | Drill-through works (Central → Region Detail) | Yes | | |
| 29 | Dashboard | Usability check passed | Yes | | |

**Validated when:** every row is *Pass*. Only then: tick the Power BI items in `PROJECT_CHECKLIST.md`, change the README status, and say "validated" in interviews.

---

## After validation: screenshots

1. Hide the `Validation` page (right-click its tab → *Hide page*). Click the **Reset filters** button (Year = 2024).
2. For each of the 5 pages: *View → Page view → Fit to page* → press **Win + Shift + S** → drag over the canvas → paste into Paint (or click the Snipping Tool notification) → *Save as PNG* into the project's `screenshots\` folder:
   `01_executive_overview.png` · `02_regional_performance.png` · `03_product_performance.png` · `04_customer_performance.png` · `05_profitability_discount.png`
3. Optional: *File → Export → Export to PDF* → `powerbi\Regional_Sales_Dashboard.pdf`, viewable without Power BI.
4. *File → Save* the `.pbix`.

## After validation: README and GitHub

1. In `README.md`, under **Screenshots**, add:
   ```markdown
   ![Executive Overview](screenshots/01_executive_overview.png)
   ```
2. In the README's Power BI section, change the status line to say the report is built and validated (include the date).
3. In `PROJECT_CHECKLIST.md`, tick the Power BI items you completed.
4. Commit and push ([docs/GITHUB_PUBLISHING.md](../docs/GITHUB_PUBLISHING.md) §5):
   ```bash
   git add powerbi/Regional_Sales_Dashboard.pbix powerbi/FINAL_VALIDATION.md screenshots/*.png README.md PROJECT_CHECKLIST.md
   git commit -m "Add Power BI dashboard, validation results and screenshots"
   git push
   ```
   Committing this file with the *Actual* column filled in is good evidence for recruiters.
