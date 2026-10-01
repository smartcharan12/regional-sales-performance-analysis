# DAX Validation Checklist

> ## ⚠️ Power BI Desktop validation required
> None of these measures has been executed yet: Power BI Desktop is Windows-only and this project was prepared on Linux.
> **Verified:** every expected value below was computed in Python from `data/processed/sales_cleaned.csv`, and the headline values were confirmed in MySQL 8 (identical to the cent). Every `Table[Column]` in the DAX matches the CSV headers.
> **Your job:** create each measure in the order below ([POWER_BI_MASTER_GUIDE.md › Part F](POWER_BI_MASTER_GUIDE.md#part-f-dax-measures-all-31-in-build-order) has the exact DAX), validate it, and change ☐ to ☑.

## How to validate (read once)

1. Build the **Validation** page first ([Master Guide F3](POWER_BI_MASTER_GUIDE.md#f3-the-validation-page-build-it-first)). It holds **table 1**, measures with no rows (no filter), and **table 2**, whose first column is `DimDate[Year]` or `DimGeography[Region]` (one row per year or region). This page has **no slicers** and is excluded from slicer sync.
2. **"No filter"** means nothing is selected anywhere. The value is the whole dataset, 2021–2024.
3. **"Table by Year / by Region"** means read the value in that row of table 2.
4. **"Year = 2024"** without a table means: add a *page-level filter* (*Filters pane → Filters on this page → drag `DimDate[Year]` → tick 2024*), read the value, then remove the filter.
5. Values are rounded to 2 decimals. A difference in the last digit is formatting. Anything larger means something is wrong → [POWER_BI_TROUBLESHOOTING.md](POWER_BI_TROUBLESHOOTING.md).

## The 31 measures

| # | Measure | Expected Result | How to Validate | Status |
|---|---|---|---|---|
| 1 | Total Sales | No filter: **4,391,176.00**. By year: 2021 1,045,575.54 · 2022 1,035,179.93 · 2023 1,117,829.65 · 2024 1,192,590.88. By region: West 1,512,745.30 · East 1,195,924.92 · Central 892,318.30 · South 790,187.48. | Validation page: table 1 (no filter); table 2 with `DimDate[Year]`; then swap in `DimGeography[Region]`. The table total must also read 4,391,176.00. | ☐ |
| 2 | Total Profit | No filter: **452,068.04**. 2024: 110,241.76. Central: 29,294.54. Category Furniture: −1,797.48. | Add to both validation tables; for Furniture, add `DimProduct[Category]` as rows. | ☐ |
| 3 | Total Quantity | No filter: **56,703**. 2024: 15,341. | Add to the validation tables. | ☐ |
| 4 | Total Orders | No filter: **5,190**. By year: 1,184 · 1,260 · 1,353 · 1,393. By region: West 1,731 · East 1,422 · Central 1,131 · South 906. | Validation tables. If you see 11,461, you counted lines. | ☐ |
| 5 | Order Lines | No filter: **11,461**. | Must equal the FactSales row count from B6. | ☐ |
| 6 | Customers | No filter: **741**. West 240 · East 218 · Central 152 · South 131. Segments: Consumer 406 · Corporate 189 · Home Office 146. Year 2024: 544. | Validation tables by Region / Segment / Year. | ☐ |
| 7 | Profit Margin % | No filter: **10.29%**. 2024: 9.24%. East 13.23% · West 12.27% · South 10.00% · Central 3.28%. Central + 2024: −0.37%. | Validation tables. **11.74%** means you averaged a column. Use this measure. | ☐ |
| 8 | Average Order Value | No filter: **846.08**. By year: 883.09 · 821.57 · 826.19 · 856.13. | Validation tables. 383.14 means you averaged line sales instead. | ☐ |
| 9 | Sales per Customer | No filter: **5,926.01**. Year 2024: 2,192.26. | Validation table 1; table 2 by Year. | ☐ |
| 10 | Gross Sales | No filter: **5,196,678.83**. | Validation table 1. | ☐ |
| 11 | Discount Amount | No filter: **805,502.83**. | Gross Sales − Total Sales must equal this. | ☐ |
| 12 | Effective Discount % | No filter: **15.50%**. By year: 15.07% · 15.06% · 15.59% · 16.17%. Central 21.51% · South 15.01% · West 13.47% · East 13.46%. Central + 2024: 23.68%. | Validation tables by Year / Region. | ☐ |
| 13 | Company Margin | No filter: **10.29%**. Year 2024: 9.24%. Unchanged when a Region is selected. | Table 2 by Region: every row shows 10.29%. | ☐ |
| 14 | Margin vs Company | Table by Region, no Year filter: Central **−7.01** · South −0.30 · West 1.97 · East 2.94. | Table 2 by Region. | ☐ |
| 15 | Sales Share % | Table by Region, no filter: West **34.45%** · East 27.23% · Central 20.32% · South 17.99%; total 100%. | Table 2 by Region. | ☐ |
| 16 | Sales PY | Table by Year: 2021 blank · 2022 1,045,575.54 · 2023 1,035,179.93 · 2024 **1,117,829.65**. | Table 2 by Year: each row equals the previous row's Total Sales. Blank everywhere = date table not marked (E1). | ☐ |
| 17 | YoY Sales Growth % | Table by Year: 2021 blank · 2022 −0.99% · 2023 7.98% · 2024 **6.69%**. No year filter (card): **blank**, by design. Region rows with Year = 2024: East 25.76% · West 12.07% · Central −12.05% · South −12.18%. | Table 2 by Year; for regions, use a table by Region with a page-level filter Year = 2024 on the Validation page. | ☐ |
| 18 | Profit PY | Table by Year: 2022 112,678.34 · 2023 111,076.75 · 2024 **118,071.19**. Central with Year = 2024: 7,701.14. | Table 2 by Year. | ☐ |
| 19 | YoY Profit Growth % | Table by Year: 2022 −1.42% · 2023 6.30% · 2024 **−6.63%**. Central with Year = 2024: −109.66%. | Table 2 by Year. | ☐ |
| 20 | Profit Margin PY | Table by Year: 2021 blank · 2022 10.78% · 2023 10.73% · 2024 **10.56%**. | Table 2 by Year: each row equals the previous row's Profit Margin %. | ☐ |
| 21 | Growth Gap (pp) | Table by Year: 2022 −0.43 · 2023 −1.69 · 2024 **−13.32**. | Table 2 by Year. | ☐ |
| 22 | Sales YTD | Matrix rows `DimDate[Year]` → `DimDate[Month]`: 2024 Jun **432,839.63**; 2024 Dec 1,192,590.88 (= full year). | Add a Matrix to the Validation page, expand 2024. | ☐ |
| 23 | Region Rank | Table by Region, no filter: West 1 · East 2 · Central 3 · South 4; total row blank. | Table 2 by Region. | ☐ |
| 24 | Top Region | No filter: **West**. Year 2024: West. | Put it in a Card on the Validation page. | ☐ |
| 25 | Top Category | No filter: **Technology**. Year 2024: Technology. | Card. | ☐ |
| 26 | Loss-Making Lines | No filter: **1,907**. | Validation table 1. | ☐ |
| 27 | Loss Line % | No filter: **16.64%**. Year 2024: 16.95%. | Validation tables. | ☐ |
| 28 | Deep Discount Profit | No filter: **−249,356.36**. Central: −96,101.03. Year 2024: −81,467.69. | Validation tables by Region / Year. | ☐ |
| 29 | Max Uplift (Cap 20%) | No filter: **264,266.66**. Central 102,178.76 · West 71,258.06 · East 48,015.61 · South 42,814.23. Year 2024: 83,691.16. | Validation tables by Region / Year. | ☐ |
| 30 | High Sales Low Margin | Table of `DimProduct[Product Name]` filtered to flag = 1 (no slicers): **8 rows**: Round Table M702, Folding Work Table C380, Training Table D848, Rectangular Table R527, 3-Shelf Shelving Unit M597, Open Shelving Unit T373, Training Table W359, Orbit Smartphone L502. | Validation page: Table with Product Name + this measure; visual filter `High Sales Low Margin is 1`. | ☐ |
| 31 | Margin Color | Table by Region (no filter): Central and South `#EC835A` (below 10.29%), East and West `#2A78D6`. By Sub-Category: Tables, Bookcases, Supplies `#D03B3B`. | Table 2 by Region; then by Sub-Category. | ☐ |

## Values that depend on filter context: what "correct" means

| Measure | Why there's no single number | The correct check |
|---|---|---|
| YoY Sales Growth %, YoY Profit Growth % | Return BLANK unless **exactly one** year is in context (guarded by `HASONEVALUE`) | In a table by Year, compare each row with the Python results above. A card with no Year selected **should** be blank |
| Sales PY, Profit PY, Profit Margin PY | Shift the selected dates back one year; 2021 has no previous year | Each Year row must equal the **previous row's** Total Sales / Total Profit / Profit Margin % |
| Sales YTD | Running total that restarts every January | For 2024, December YTD must equal 2024 Total Sales (1,192,590.88); June must be 432,839.63 |
| Sales Share %, Region Rank | Relative to the regions **currently selected** (`ALLSELECTED`) | With no filter: shares add up to 100% and ranks are 1–4. With Region = Central only: share 100%, rank 1 (correct, not a bug) |
| Company Margin, Margin vs Company | Ignore region/product/customer filters but **respect dates** | Selecting Central doesn't change Company Margin; selecting Year = 2024 changes it to 9.24% |
| Top Region, Top Category | Text; depend on all filters | No filter: West / Technology |
| High Sales Low Margin | Ranks products within the current selection | With no slicers: exactly the 8 products listed. With a Category slicer the list legitimately changes |
| Margin Color | Returns a colour code, not a number | Check the colours on the charts, not the text |

## Common mistakes (quick reference)

| Symptom | Likely cause |
|---|---|
| Total Sales shows an error or "Count of Sales" | `Sales` loaded as Text, or you dragged the column instead of the measure |
| Total Orders = 11,461 | Used `COUNTROWS`/`COUNT` instead of `DISTINCTCOUNT(FactSales[Order ID])` |
| Profit Margin = 11.74% | Averaged a row-level margin column instead of using the measure |
| Average Order Value = 383.14 | Used `AVERAGE(FactSales[Sales])` (average line, not average order) |
| Sales PY blank everywhere | `DimDate` not marked as date table, or the relationship to `FactSales[Order Date]` is missing |
| YoY blank on a card | More than one year (or none) selected. This is correct behaviour |
| Every region shows Region Rank = 1 | `ALLSELECTED` missing from the formula |
| Customers always 741 | Counted `DimCustomer` rows instead of `DISTINCTCOUNT(FactSales[Customer ID])` |

Full symptom → cause → fix → verify list: [POWER_BI_TROUBLESHOOTING.md](POWER_BI_TROUBLESHOOTING.md). Formula explanations: [DAX_Measures.md](DAX_Measures.md).

## Sign-off

- [ ] All 31 measures created, with no formula errors (no yellow ⚠ in the *Data* pane)
- [ ] All 31 rows above set to ☑
- [ ] The *Validation* page hidden before publishing
