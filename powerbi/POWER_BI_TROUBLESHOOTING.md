# Power BI Troubleshooting

Each problem: **SYMPTOM → CAUSE → FIX → HOW TO VERIFY.** Section numbers are referenced from [POWER_BI_MASTER_GUIDE.md](POWER_BI_MASTER_GUIDE.md).

> Written without access to Power BI Desktop (Linux environment). The causes and fixes are standard Power BI behaviour, but exact menu labels may differ slightly between versions. Use the search box at the top of Power BI if a menu has moved.

**Golden rule:** fix problems in the order *data → model → measures → visuals*. A wrong chart is usually caused by a wrong data type or relationship further upstream.

---

### 1. CSV cannot be found
* **SYMPTOM:** Power Query shows *DataSource.NotFound: File or Folder: We couldn't find the file …\FactSales.csv*.
* **CAUSE:** the `DataFolder` parameter points to a folder that doesn't exist on this PC, or the CSVs aren't in it.
* **FIX:** in File Explorer, confirm the five files exist in `…\regional-sales-performance-analysis\data\processed\powerbi\`. If the folder is empty, the repository wasn't copied completely: copy it again, or run `python src/pipeline.py`. Then fix the parameter (§2).
* **HOW TO VERIFY:** *Transform data* → click `FactSales` → the preview shows rows. *Home → Refresh preview* raises no error.

### 2. DataFolder parameter incorrect
* **SYMPTOM:** the error message shows a path like `…\powerbiFactSales.csv` (no backslash before the file name), or a folder from another PC.
* **CAUSE:** missing trailing `\`, a typo, or quotation marks pasted into the value.
* **FIX:** *Transform data → Home → Manage Parameters → DataFolder → Current Value* = the full folder path ending in `\`, without quotes. *OK → Close & Apply*.
* **HOW TO VERIFY:** all five queries preview without errors; after *Close & Apply*, the row counts are 11,461 / 1,461 / 741 / 174 / 36.

### 3. Wrong Windows path
* **SYMPTOM:** "file not found", although the files exist.
* **CAUSE:** the path was typed by hand (`Document` vs `Documents`), uses `/` instead of `\`, points into a ZIP file that wasn't extracted, or points to a OneDrive file that is "online-only".
* **FIX:** copy the path from the File Explorer address bar; extract ZIP downloads first; for OneDrive folders, right-click the folder → *Always keep on this device*.
* **HOW TO VERIFY:** paste the path + `FactSales.csv` into File Explorer's address bar; the file opens or is offered for download.

### 4. Relationships not created
* **SYMPTOM:** a slicer on Region, Year or Category changes nothing, or every row of a table by Region shows the same total (4,391,176.00).
* **CAUSE:** the relationship between that dimension and `FactSales` is missing, or wasn't saved.
* **FIX:** **Model view** → *Home → Manage relationships* → confirm all four exist exactly as in [Master Guide D2](POWER_BI_MASTER_GUIDE.md#d2-create-the-four-relationships). Create any missing one.
* **HOW TO VERIFY:** a table with `DimGeography[Region]` + `[Total Sales]` shows West 1,512,745.30 · East 1,195,924.92 · Central 892,318.30 · South 790,187.48.

### 5. Relationship says many-to-many
* **SYMPTOM:** the relationship dialog shows *Many to many (\*:\*)*, or warns that "neither column has unique values".
* **CAUSE:** you linked the wrong columns (e.g. `DimGeography[Region]` → `FactSales[…]`), or the dimension column isn't unique because it was loaded from the wrong file (e.g. `sales_cleaned.csv`).
* **FIX:** delete the relationship and recreate it with the exact key columns: `DimDate[Date]`, `DimCustomer[Customer ID]`, `DimProduct[Product ID]`, `DimGeography[GeoKey]` on the "one" side. Check the dimension row counts (741 / 174 / 36 / 1,461).
* **HOW TO VERIFY:** the relationship line shows **1** at the dimension and **\*** at `FactSales`.

### 6. Date table not recognised
* **SYMPTOM:** *Mark as date table* is greyed out or rejected ("contains duplicates/blanks"), or `Sales PY` is blank everywhere.
* **CAUSE:** `DimDate[Date]` is Text instead of Date; the table was filtered so dates are missing; or the relationship uses another column.
* **FIX:** set `DimDate[Date]` to type **Date** (Master Guide Part C); remove any filter step on `DimDate` in Power Query (1,461 rows required); mark it again (Part E1); make sure relationship 1 is `DimDate[Date]` → `FactSales[Order Date]`.
* **HOW TO VERIFY:** table by `DimDate[Year]` with `[Sales PY]`: 2024 row = **1,117,829.65**.

### 7. DAX syntax error
* **SYMPTOM:** red squiggle; message like *"The syntax for ',' is incorrect"* or *"Unexpected end of input"*.
* **CAUSE:** a bracket or comma lost while pasting; curly "smart quotes" pasted from a word processor; a comment line broken across lines; or a regional setting that uses `;` as the list separator.
* **FIX:** copy the DAX again from [Master Guide Part F](POWER_BI_MASTER_GUIDE.md#part-f-dax-measures-all-31-in-build-order) directly (not via Word). Replace `“ ”` with straight quotes `"`. If your Power BI expects `;`, either switch *File → Options → Global → Regional settings → "Use recommended settings…"* to English (US), or replace `,` with `;` between arguments.
* **HOW TO VERIFY:** the formula bar shows no squiggles and the measure appears with a calculator icon.

### 8. Column not found
* **SYMPTOM:** *"Column 'OrderID' in table 'FactSales' cannot be found"*, or *"The name 'Sales' does not exist"*.
* **CAUSE:** a misspelled name. Column names contain spaces and hyphens: `Order ID`, `Gross Sales`, `Discount Amount`, `Sub-Category`, `Year-Month`. Or the query was renamed (e.g. `FactSales (2)`).
* **FIX:** use exactly `FactSales[Order ID]`, etc. Rename queries to the exact five names. Tip: type `FactSales[` and choose from the autocomplete list.
* **HOW TO VERIFY:** the measure creates without error and `[Total Orders]` = **5,190**.

### 9. Measure returns blank
* **SYMPTOM:** a card or table cell shows *(Blank)*.
* **CAUSE:** (a) the filters exclude all rows (e.g. a Region slicer plus a Category with no sales there); (b) a missing relationship; (c) a time-intelligence measure with no previous year (2021); (d) a YoY measure with several years selected (see §10); (e) a `Sales` column loaded as text.
* **FIX:** clear all slicers (eraser icons) and check again; then check relationships (§4) and data types (§16).
* **HOW TO VERIFY:** on the unfiltered Validation page, `[Total Sales]` = 4,391,176.00.

### 10. YoY returns blank
* **SYMPTOM:** `YoY Sales Growth %` / `YoY Profit Growth %` show blank on a card.
* **CAUSE:** **by design**, they need exactly one year in context (`HASONEVALUE(DimDate[Year])`). With no year or several years selected they return blank, because "all years vs all years minus one" is meaningless. 2021 is also blank (no 2020 data). If blank even with one year selected: the date table isn't marked (§6).
* **FIX:** select a single year in the Year slicer (e.g. 2024). For a table, put `DimDate[Year]` in the rows.
* **HOW TO VERIFY:** Year = 2024 → YoY Sales **6.69%**, YoY Profit **−6.63%**.

### 11. Wrong total sales
* **SYMPTOM:** Total Sales isn't 4,391,176.00 with no filters.

| Value you see | Cause | Fix |
|---|---|---|
| An error, or a total that isn't 4,391,176.00 | Imported `sales_raw.csv` (contains duplicates, invalid rows and text like `"$1,277.10"`) instead of `FactSales.csv` | Re-point the query to `DataFolder & "FactSales.csv"` |
| A count (e.g. 11,461) | Dragged the column, so it was summarised as Count | Use the measure `[Total Sales]` |
| ~1.19M | A Year slicer / page filter is set to 2024 | Clear filters |
| 100× too big, or decimals lost | Locale misread `207.3` | Use the M code with the `"en-US"` culture (Master Guide B5) |
| Error | `Sales` is Text | Set it to Fixed decimal number |

* **HOW TO VERIFY:** the Validation page shows **4,391,176.00**, the FactSales row count is 11,461, and Total Orders = 5,190.

### 12. Wrong profit margin
* **SYMPTOM:** company margin isn't 10.29%.
* **CAUSE:** **11.74%** means a row-level margin column was averaged. Other values: Profit/Sales mixed up, or the format isn't percentage (0.10 shown as 0.10).
* **FIX:** use `Profit Margin % = DIVIDE ( [Total Profit], [Total Sales] )` and set *Format → Percentage*. Delete any calculated column that computes margin per row.
* **HOW TO VERIFY:** 10.29% with no filters; Central 3.28%; Year 2024 9.24%.

### 13. Slicer doesn't affect a chart
* **SYMPTOM:** changing the Year/Region slicer leaves one visual unchanged.
* **CAUSE:** (a) the interaction is set to **None** (intentional for the two trend charts on page 1 and the yearly chart on page 2); (b) the slicer uses a column from a table with no relationship to `FactSales`; (c) the visual uses a raw fact column, e.g. `FactSales[Order Date]` instead of `DimDate`; (d) the slicer isn't synced to that page.
* **FIX:** select the slicer → *Format → Edit interactions* → set the visual to *Filter* (except the intentional ones). Check the relationships (§4). Use dimension columns. *View → Sync slicers*: tick the page.
* **HOW TO VERIFY:** Region = Central → the page-2 scorecard shows only Central with margin 3.28% (Year cleared).

### 14. Visual shows unexpected values
* **SYMPTOM:** numbers that look plausible but don't match the expected values.
* **CAUSE:** usually **filters you forgot**: a slicer synced from another page, a page-level or visual-level filter (Top N!), or a cross-highlight left on after clicking a bar.
* **FIX:** open the *Filters* pane and check *Filters on this visual / page / all pages*. Click an empty canvas area to clear cross-highlighting. Clear the slicers. Check that the visual uses measures, not raw columns.
* **HOW TO VERIFY:** compare with the Validation page values for the same filter state ([DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md)).

### 15. Duplicate relationship
* **SYMPTOM:** two lines between the same tables, one dotted (inactive); or a warning about an *ambiguous path*.
* **CAUSE:** auto-detect created a relationship (e.g. `DimDate[Date]` → `FactSales[Ship Date]`, or `DateKey` → `OrderDateKey`) in addition to yours.
* **FIX:** *Manage relationships* → delete everything except the four in Master Guide D2. Also turn off auto-detect: *File → Options → Current File → Data Load → untick "Autodetect new relationships after data is loaded"*.
* **HOW TO VERIFY:** *Manage relationships* lists exactly four, all active.

### 16. Power Query type conversion error
* **SYMPTOM:** red bars under column headers in Power Query, or cells showing *Error*; *Close & Apply* reports errors; row counts are lower.
* **CAUSE:** (a) the locale reads `2024-03-26` or `0.4` differently; (b) `Ship Date` / `Shipping Days` are empty in 6 rows by design; (c) the wrong file is loaded.
* **FIX:** (a) make sure the `TransformColumnTypes` step ends with `"en-US"` (Master Guide B5), or change the type via *Using Locale… → English (United States)*. (b) Empty values should become `null`. If they show *Error*, select both columns → *Transform → Replace Errors* → leave empty → OK. (c) Check the `Source` step's file name.
* **HOW TO VERIFY:** no red bars; FactSales has 11,461 rows; `Ship Date` has 6 blanks (not errors).

### 17. `.pbix` works locally but fails after moving the folder
* **SYMPTOM:** after copying the project to another PC/folder (or cloning from GitHub), *Refresh* fails with "file not found".
* **CAUSE:** the `DataFolder` parameter still holds the **old absolute path**. A `.pbix` stores the parameter value, not a relative location.
* **FIX:** *Home → Transform data → Edit parameters* → set `DataFolder` to the new `…\data\processed\powerbi\` path (with the trailing `\`) → OK → *Refresh*.
* **HOW TO VERIFY:** *Refresh* completes, and the Validation page still shows 4,391,176.00.
* **Note:** opening the `.pbix` *without* refreshing still works anywhere, because the data is stored inside the file. Only *Refresh* needs the CSVs.
