# Power BI Master Guide: build the RetailCo dashboard from start to finish

**This is the one document to follow on Windows.** Open it next to Power BI Desktop and work top to bottom. Each step gives: **Click** · **Enter** · **Why** · **You should see** · **If it goes wrong**.

> ⚠️ **Status:** this guide was written in a Linux environment without Power BI Desktop. The data, the expected numbers (computed in Python and confirmed in MySQL 8) and the column names are verified. The clicks follow current Power BI Desktop menus but have **not** been performed. If a button has moved in your version, use the **search box at the top of the Power BI window**. Problems: [POWER_BI_TROUBLESHOOTING.md](POWER_BI_TROUBLESHOOTING.md). Final proof: [FINAL_VALIDATION.md](FINAL_VALIDATION.md).

**Time:** about 4–6 hours the first time. **Save often** (Ctrl + S).

Background reading (optional): [Data_Model.md](Data_Model.md) explains *why* the model looks like this; [DAX_Measures.md](DAX_Measures.md) explains every formula line by line; [Dashboard_Design.md](Dashboard_Design.md) is the design rationale behind Part G.

---

## PART A: Before opening Power BI

### A1. What you need
* A Windows PC with **Power BI Desktop** (free, from the Microsoft Store).
* This project folder on that PC (copy it, or `git clone` it after you've pushed it to GitHub).
* Nothing else. You do **not** need Python or MySQL for the Power BI part: the CSV files are already in the repository.

### A2. The files Power BI uses
Only these five files, in `data\processed\powerbi\`:

| File | Rows | One row is… | Key column(s) |
|---|---|---|---|
| `FactSales.csv` | 11,461 | one product on one order (an *order line*) | `SalesKey`; links: `Order Date`, `Customer ID`, `Product ID`, `GeoKey` |
| `DimDate.csv` | 1,461 | one calendar day, 2021-01-01 → 2024-12-31 | `Date` |
| `DimCustomer.csv` | 741 | one customer | `Customer ID` |
| `DimProduct.csv` | 174 | one product | `Product ID` |
| `DimGeography.csv` | 36 | one city | `GeoKey` |

They were produced by `python src/pipeline.py` from the cleaned data. **Do not** import `sales_raw.csv` (messy) or `sales_cleaned.csv` (the same data, but as one flat table).

### A3. What the project structure means for Power BI
```
regional-sales-performance-analysis\
├── data\processed\powerbi\   ← Power BI reads ONLY this folder
├── powerbi\                  ← this guide; save your .pbix here
└── screenshots\              ← put the dashboard screenshots here at the end
```

### A4. What Power BI will build from them
```
              DimDate (Date)
                    │ 1
                    ▼ *
DimCustomer ──1──► FactSales ◄──1── DimProduct
                    ▲ *
                    │ 1
           DimGeography (GeoKey)
```
A **star schema**: one fact table of numbers in the middle, four dimension tables of descriptions around it. You will (1) load the tables, (2) connect them, (3) write 31 formulas (*measures*), and (4) build 5 report pages plus 1 hidden detail page.

---

## PART B: Create the Power BI project

### B1. Open Power BI Desktop
**Click:** Start menu → *Power BI Desktop*. Close the welcome/sign-in pop-up (signing in isn't required).
**You should see:** an empty white canvas; on the right, panes called *Visualizations* and *Data*; on the left edge, three icons: **Report** 📊, **Table** ▦, **Model** ⧉.
**If it goes wrong:** if you're in a web browser (app.powerbi.com), that's the Service, not Desktop. Install and open the Desktop app.

### B2. Create and save a blank report
**Click:** *File → Save as* → browse to the project's `powerbi\` folder.
**Enter:** file name `Regional_Sales_Dashboard` → *Save* (the extension `.pbix` is added automatically).
**Also click:** *File → Options and settings → Options → Current File → Data Load* → **untick "Auto date/time"** → OK.
**Why:** saving early prevents lost work. Auto date/time would create hidden date tables that compete with `DimDate`.

### B3. Create the `DataFolder` parameter
**Click:** *Home → Transform data* (the **Power Query Editor** opens in a new window) → *Home → Manage Parameters → New Parameter*.
**Enter:**
* Name: `DataFolder`
* Type: `Text`
* Suggested Values: `Any value`
* Current Value: see B4
**Why:** all five tables will read from this one path. If the folder moves, you change one value instead of five queries.

### B4. Set the correct local path
**How to get the path:** in File Explorer, open `regional-sales-performance-analysis\data\processed\powerbi\` → click the address bar → copy.
**Enter** that path **plus a trailing backslash**, for example:
```
C:\Users\<your-user-name>\Documents\regional-sales-performance-analysis\data\processed\powerbi\
```
**You should see:** `DataFolder` listed under *Queries* on the left, with the path as its value.
**If it goes wrong:** forgetting the final `\` makes Power BI look for `...powerbiFactSales.csv`. See Troubleshooting §2.

### B5. Import the five CSV files
For **each** of the five tables, do this once:

**Click:** in the Power Query Editor, *Home → New Source → Blank Query* → *Home → Advanced Editor* → delete everything → paste the code below → *Done*. Then right-click the new query → *Rename*, and give it the table name exactly as shown.

**`FactSales`**
```m
let
    Source   = Csv.Document(File.Contents(DataFolder & "FactSales.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"SalesKey", Int64.Type}, {"Order ID", type text},
                   {"OrderDateKey", Int64.Type},
                   {"Order Date", type date}, {"Ship Date", type date},
                   {"Ship Mode", type text}, {"Customer ID", type text},
                   {"Product ID", type text}, {"GeoKey", Int64.Type},
                   {"Sales", Currency.Type}, {"Quantity", Int64.Type},
                   {"Discount", type number}, {"Profit", Currency.Type},
                   {"Gross Sales", Currency.Type}, {"Discount Amount", Currency.Type},
                   {"Shipping Days", Int64.Type}}, "en-US")
in
    Typed
```

**`DimDate`**
```m
let
    Source   = Csv.Document(File.Contents(DataFolder & "DimDate.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"DateKey", Int64.Type}, {"Date", type date}, {"Year", Int64.Type},
                   {"Quarter", type text}, {"Month Number", Int64.Type},
                   {"Month", type text}, {"Year-Month", type text},
                   {"Weekday", type text}, {"Is Weekend", type logical}}, "en-US")
in
    Typed
```

**`DimCustomer`**
```m
let
    Source   = Csv.Document(File.Contents(DataFolder & "DimCustomer.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"Customer ID", type text}, {"Customer Name", type text},
                   {"Segment", type text}}, "en-US")
in
    Typed
```

**`DimProduct`**
```m
let
    Source   = Csv.Document(File.Contents(DataFolder & "DimProduct.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"Product ID", type text}, {"Product Name", type text},
                   {"Category", type text}, {"Sub-Category", type text}}, "en-US")
in
    Typed
```

**`DimGeography`** (includes the extra `State Location` column for maps)
```m
let
    Source   = Csv.Document(File.Contents(DataFolder & "DimGeography.csv"),
                   [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
                   {"GeoKey", Int64.Type}, {"Country", type text}, {"Region", type text},
                   {"State", type text}, {"City", type text}}, "en-US"),
    AddLocation = Table.AddColumn(Typed, "State Location",
                   each [State] & ", United States", type text)
in
    AddLocation
```

**Why the code instead of clicking *Get data → Text/CSV*?** It does the same thing, but also uses `DataFolder` and sets every data type in one step, with the US locale (so `2024-03-26` and `0.4` are read correctly on any Windows language setting). `State Location` stops maps from placing "Georgia" in the country Georgia.

**You should see:** five queries with these exact names: `FactSales`, `DimDate`, `DimCustomer`, `DimProduct`, `DimGeography` (plus `DataFolder`). Click each one; the preview shows data, not errors.

### B6. Load and check row counts
**Click:** *Home → Close & Apply*. Wait for loading to finish. Then click the **Table view** ▦ icon (left edge), and click each table in the *Data* pane: the row count is shown at the bottom-left.

| Table | Expected rows |
|---|---|
| FactSales | **11,461** |
| DimDate | **1,461** |
| DimCustomer | **741** |
| DimProduct | **174** |
| DimGeography | **36** |

**If it goes wrong:** different counts → Troubleshooting §16.

---

## PART C: Data types

The M code in B5 sets these automatically. **Check** them in Table view: select a column, and its type is shown under *Column tools → Data type*.

| Table | Column | Data type in Power BI | Format |
|---|---|---|---|
| FactSales | `SalesKey`, `OrderDateKey`, `GeoKey`, `Quantity`, `Shipping Days` | Whole number | |
| FactSales | `Order Date`, `Ship Date` | Date | yyyy-mm-dd |
| FactSales | `Order ID`, `Ship Mode`, `Customer ID`, `Product ID` | Text | |
| FactSales | `Sales`, `Profit`, `Gross Sales`, `Discount Amount` | Fixed decimal number | Currency |
| FactSales | `Discount` | Decimal number | Percentage (optional) |
| DimDate | `Date` | Date | |
| DimDate | `DateKey`, `Year`, `Month Number` | Whole number | |
| DimDate | `Quarter`, `Month`, `Year-Month`, `Weekday` | Text | |
| DimDate | `Is Weekend` | True/false | |
| DimCustomer | all three columns | Text | |
| DimProduct | all four columns | Text | |
| DimGeography | `GeoKey` | Whole number | |
| DimGeography | `Country`, `Region`, `State`, `City`, `State Location` | Text | |

**Data categories (for maps):** select `DimGeography[State]` → *Column tools → Data category → State or Province*; `[City]` → *City*; `[State Location]` → *Place*.

**Expected blanks:** 6 rows of `FactSales` have an empty `Ship Date` and `Shipping Days`. This is intentional: impossible ship dates were blanked during cleaning. They must be blank, not errors.

**Also set `Year` to "Don't summarize":** select `DimDate[Year]` → *Column tools → Summarization → Don't summarize*. Otherwise Power BI may add the years up (e.g. 2021 + 2022…).

---

## PART D: Relationships

### D1. The ideas (read once)
* **Primary key (PK):** a column whose value is **unique** in its table, e.g. `DimProduct[Product ID]`. Each product appears once.
* **Foreign key (FK):** the same column in the fact table, `FactSales[Product ID]`, pointing back to that one product. It repeats, because a product is sold many times.
* **One-to-many (1 : \*):** one product row ↔ many sales rows. The "one" side must be unique, otherwise Power BI can't tell which description a sale belongs to.
* **Single-direction filter (dimension → fact):** when you pick "Technology" (a `DimProduct` value), Power BI keeps only the Technology `Product ID`s, follows the arrow into `FactSales`, keeps only those sales, and recalculates. Filters don't flow back from facts to dimensions, which keeps the model predictable and fast.
* **Why dimensions filter the fact table:** people think in descriptions ("Central", "2024", "Furniture"), and those live in dimensions. The numbers live in the fact table. A relationship is the bridge.

### D2. Create the four relationships
**Click:** the **Model view** ⧉ icon. Power BI may already have drawn some lines automatically. Open *Home → Manage relationships* and **delete every existing relationship** (select → *Delete*), then create the four below. Either drag the dimension column onto the fact column in the diagram, or use *Manage relationships → New*:

| # | From: table[column] (one side, PK) | To: table[column] (many side, FK) | Cardinality | Cross filter direction | Active |
|---|---|---|---|---|---|
| 1 | `DimDate[Date]` | `FactSales[Order Date]` | One to many (1:\*) | Single | ✔ |
| 2 | `DimCustomer[Customer ID]` | `FactSales[Customer ID]` | One to many (1:\*) | Single | ✔ |
| 3 | `DimProduct[Product ID]` | `FactSales[Product ID]` | One to many (1:\*) | Single | ✔ |
| 4 | `DimGeography[GeoKey]` | `FactSales[GeoKey]` | One to many (1:\*) | Single | ✔ |

In the *New relationship* dialog: top table = the dimension, bottom table = `FactSales`, select the matching column in each, Cardinality *One to many*, Cross filter direction *Single*, ✔ *Make this relationship active* → OK.

**You should see:** exactly four solid lines, each with **1** at the dimension and **\*** at `FactSales`, and a small arrow pointing toward `FactSales`.
**Do not** create a relationship on `Ship Date`, `OrderDateKey` or `DateKey`.
**If it goes wrong:** many-to-many, dotted lines or duplicates → Troubleshooting §4–5, §15.

### D3. Hide the key columns
In Model view or the Data pane, right-click each column → *Hide in report view*:
`FactSales[SalesKey]`, `FactSales[OrderDateKey]`, `FactSales[GeoKey]`, `FactSales[Customer ID]`, `FactSales[Product ID]`, `FactSales[Order Date]`, `DimDate[DateKey]`, `DimGeography[GeoKey]`.
**Why:** report builders should filter with dimension columns (`DimDate[Year]`, `DimGeography[Region]`). Hiding `FactSales[Order Date]` prevents accidentally bypassing the date table.

---

## PART E: The date table

### E1. Mark `DimDate` as the date table
**Click:** in the *Data* pane, select the table `DimDate` (click its name) → ribbon *Table tools → Mark as date table* → in the dialog choose **Date column: `Date`** → *OK* (newer versions: switch *Mark as a date table* **On**, then pick `Date`).
**Why:** time-intelligence functions (`SAMEPERIODLASTYEAR`, `TOTALYTD`) need to know which table is the official calendar. Power BI validates that `Date` is unique and has no gaps.
**You should see:** a confirmation, with no warnings. `DimDate` has 1,461 consecutive days, every day of 2021–2024.
**If it goes wrong:** the option is greyed out or rejected → Troubleshooting §6.

### E2. Sort month names correctly
**Click:** select `DimDate[Month]` → *Column tools → Sort by column → `Month Number`*.
**Why:** otherwise charts show Apr, Aug, Dec, Feb… (alphabetical).
`Year-Month` (e.g. `2024-03`) already sorts correctly as text.

---

## PART F: DAX measures (all 31, in build order)

### F1. Where measures live
**Click:** *Home → Enter data* → change the table name to `_Measures` → *Load*. A table with one empty column appears. After creating your first measure you may delete that column (`Column1`); the table then shows a calculator icon and moves to the top of the Data pane.

### F2. How to create each measure
1. Click `_Measures` in the *Data* pane.
2. *Home → New measure* (or *Table tools → New measure*).
3. In the formula bar, delete the placeholder text and paste the DAX **exactly** as shown below → press **Enter**.
4. Set the format in the *Measure tools* ribbon (Format, decimal places), as listed for each measure.
5. **Validate immediately** (method given for each measure), then tick it in [DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md).

**Create them in this order**: later measures use earlier ones, and a measure that refers to one not yet created shows an error.

### F3. The validation page (build it first)
**Click:** add a page with **+** at the bottom → double-click its tab → rename it `Validation`. Insert a *Table* visual (*Visualizations → Table*). You'll drop measures into its *Columns* well as you create them. For "with filter" checks, add `DimDate[Year]` or `DimGeography[Region]` as the first column of a **second** table, so you see one row per year or region.
On this page only, **don't** add slicers. The "no filter" values below assume nothing is filtered.

> **Filter context in one sentence:** a measure is written once, and Power BI recalculates it for each cell using whatever filters apply there (slicers, the row of a table, a bar of a chart). The "Filter" column in each entry tells you which context the expected value belongs to.

#### F1. Total Sales
```dax
Total Sales = SUM ( FactSales[Sales] )
```
* **Purpose:** Revenue after discount.
* **Format:** Currency, 2 dp
* **Expected:** No filter: **4,391,176.00**. By year: 2021 1,045,575.54 · 2022 1,035,179.93 · 2023 1,117,829.65 · 2024 1,192,590.88. By region: West 1,512,745.30 · East 1,195,924.92 · Central 892,318.30 · South 790,187.48.
* **Validate:** Validation page: table 1 (no filter); table 2 with `DimDate[Year]`; then swap in `DimGeography[Region]`. The table total must also read 4,391,176.00.

#### F2. Total Profit
```dax
Total Profit = SUM ( FactSales[Profit] )
```
* **Purpose:** Sales minus cost of goods (can be negative).
* **Format:** Currency, 2 dp
* **Expected:** No filter: **452,068.04**. 2024: 110,241.76. Central: 29,294.54. Category Furniture: −1,797.48.
* **Validate:** Add to both validation tables; for Furniture, add `DimProduct[Category]` as rows.

#### F3. Total Quantity
```dax
Total Quantity = SUM ( FactSales[Quantity] )
```
* **Purpose:** Units sold.
* **Format:** Whole number
* **Expected:** No filter: **56,703**. 2024: 15,341.
* **Validate:** Add to the validation tables.

#### F4. Total Orders
```dax
Total Orders = DISTINCTCOUNT ( FactSales[Order ID] )
```
* **Purpose:** Distinct orders (not lines).
* **Format:** Whole number
* **Expected:** No filter: **5,190**. By year: 1,184 · 1,260 · 1,353 · 1,393. By region: West 1,731 · East 1,422 · Central 1,131 · South 906.
* **Validate:** Validation tables. If you see 11,461, you counted lines.

#### F5. Order Lines
```dax
Order Lines = COUNTROWS ( FactSales )
```
* **Purpose:** Rows in FactSales (order lines).
* **Format:** Whole number
* **Expected:** No filter: **11,461**.
* **Validate:** Must equal the FactSales row count from B6.

#### F6. Customers
```dax
Customers = DISTINCTCOUNT ( FactSales[Customer ID] )
```
* **Purpose:** Customers who bought in the current selection.
* **Format:** Whole number
* **Expected:** No filter: **741**. West 240 · East 218 · Central 152 · South 131. Segments: Consumer 406 · Corporate 189 · Home Office 146. Year 2024: 544.
* **Validate:** Validation tables by Region / Segment / Year.

#### F7. Profit Margin %
```dax
Profit Margin % =
DIVIDE ( [Total Profit], [Total Sales] )
```
* **Purpose:** Profit per $1 of sales (weighted).
* **Format:** Percentage, 2 dp
* **Expected:** No filter: **10.29%**. 2024: 9.24%. East 13.23% · West 12.27% · South 10.00% · Central 3.28%. Central + 2024: −0.37%.
* **Validate:** Validation tables. **11.74%** means you averaged a column. Use this measure.

#### F8. Average Order Value
```dax
Average Order Value =
DIVIDE ( [Total Sales], [Total Orders] )
```
* **Purpose:** Revenue per order.
* **Format:** Currency, 2 dp
* **Expected:** No filter: **846.08**. By year: 883.09 · 821.57 · 826.19 · 856.13.
* **Validate:** Validation tables. 383.14 means you averaged line sales instead.

#### F9. Sales per Customer
```dax
Sales per Customer = DIVIDE ( [Total Sales], [Customers] )
```
* **Purpose:** Revenue per active customer.
* **Format:** Currency, 2 dp
* **Expected:** No filter: **5,926.01**. Year 2024: 2,192.26.
* **Validate:** Validation table 1; table 2 by Year.

#### F10. Gross Sales
```dax
Gross Sales     = SUM ( FactSales[Gross Sales] )
```
* **Purpose:** Value at full list price (before discount).
* **Format:** Currency, 2 dp
* **Expected:** No filter: **5,196,678.83**.
* **Validate:** Validation table 1.

#### F11. Discount Amount
```dax
Discount Amount = SUM ( FactSales[Discount Amount] )
```
* **Purpose:** Revenue given away by discounts.
* **Format:** Currency, 2 dp
* **Expected:** No filter: **805,502.83**.
* **Validate:** Gross Sales − Total Sales must equal this.

#### F12. Effective Discount %
```dax
Effective Discount % =
DIVIDE ( [Discount Amount], [Gross Sales] )
```
* **Purpose:** Share of list value given away (money-weighted).
* **Format:** Percentage, 2 dp
* **Expected:** No filter: **15.50%**. By year: 15.07% · 15.06% · 15.59% · 16.17%. Central 21.51% · South 15.01% · West 13.47% · East 13.46%. Central + 2024: 23.68%.
* **Validate:** Validation tables by Year / Region.

#### F13. Company Margin
```dax
Company Margin =
CALCULATE (
    [Profit Margin %],
    REMOVEFILTERS ( DimGeography ),
    REMOVEFILTERS ( DimProduct ),
    REMOVEFILTERS ( DimCustomer )
)
```
* **Purpose:** Whole-company margin for the selected dates (benchmark).
* **Format:** Percentage, 2 dp
* **Expected:** No filter: **10.29%**. Year 2024: 9.24%. Unchanged when a Region is selected.
* **Validate:** Table 2 by Region: every row shows 10.29%.

#### F14. Margin vs Company
```dax
Margin vs Company = ( [Profit Margin %] - [Company Margin] ) * 100
```
* **Purpose:** Selection margin minus company margin, in percentage points.
* **Format:** Decimal number, 2 dp
* **Expected:** Table by Region, no Year filter: Central **−7.01** · South −0.30 · West 1.97 · East 2.94.
* **Validate:** Table 2 by Region.

#### F15. Sales Share %
```dax
Sales Share % =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALLSELECTED ( DimGeography[Region] ) )
)
```
* **Purpose:** Share of the selected regions' total.
* **Format:** Percentage, 2 dp
* **Expected:** Table by Region, no filter: West **34.45%** · East 27.23% · Central 20.32% · South 17.99%; total 100%.
* **Validate:** Table 2 by Region.

#### F16. Sales PY
```dax
Sales PY =
CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
```
* **Purpose:** Same measure, one year earlier.
* **Format:** Currency, 2 dp
* **Expected:** Table by Year: 2021 blank · 2022 1,045,575.54 · 2023 1,035,179.93 · 2024 **1,117,829.65**.
* **Validate:** Table 2 by Year: each row equals the previous row's Total Sales. Blank everywhere = date table not marked (E1).

#### F17. YoY Sales Growth %
```dax
YoY Sales Growth % =
VAR CurrentSales = [Total Sales]
VAR PreviousSales = [Sales PY]
RETURN
    IF (
        HASONEVALUE ( DimDate[Year] ) && NOT ISBLANK ( PreviousSales ),
        DIVIDE ( CurrentSales - PreviousSales, PreviousSales )
    )
```
* **Purpose:** Growth vs previous year (only when exactly one year is in context).
* **Format:** Percentage, 2 dp
* **Expected:** Table by Year: 2021 blank · 2022 −0.99% · 2023 7.98% · 2024 **6.69%**. No year filter (card): **blank**, by design. Region rows with Year = 2024: East 25.76% · West 12.07% · Central −12.05% · South −12.18%.
* **Validate:** Table 2 by Year; for regions, use a table by Region with a page-level filter Year = 2024 on the Validation page.

#### F18. Profit PY
```dax
Profit PY =
CALCULATE ( [Total Profit], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
```
* **Purpose:** Profit one year earlier.
* **Format:** Currency, 2 dp
* **Expected:** Table by Year: 2022 112,678.34 · 2023 111,076.75 · 2024 **118,071.19**. Central with Year = 2024: 7,701.14.
* **Validate:** Table 2 by Year.

#### F19. YoY Profit Growth %
```dax
YoY Profit Growth % =
VAR CurrentProfit = [Total Profit]
VAR PreviousProfit = [Profit PY]
RETURN
    IF (
        HASONEVALUE ( DimDate[Year] ) && NOT ISBLANK ( PreviousProfit ),
        DIVIDE ( CurrentProfit - PreviousProfit, ABS ( PreviousProfit ) )
    )
```
* **Purpose:** Profit growth vs previous year (ABS denominator).
* **Format:** Percentage, 2 dp
* **Expected:** Table by Year: 2022 −1.42% · 2023 6.30% · 2024 **−6.63%**. Central with Year = 2024: −109.66%.
* **Validate:** Table 2 by Year.

#### F20. Profit Margin PY
```dax
Profit Margin PY = DIVIDE ( [Profit PY], [Sales PY] )
```
* **Purpose:** Last year's margin for the same selection.
* **Format:** Percentage, 2 dp
* **Expected:** Table by Year: 2021 blank · 2022 10.78% · 2023 10.73% · 2024 **10.56%**.
* **Validate:** Table 2 by Year: each row equals the previous row's Profit Margin %.

#### F21. Growth Gap (pp)
```dax
Growth Gap (pp) = ( [YoY Profit Growth %] - [YoY Sales Growth %] ) * 100
```
* **Purpose:** Profit growth minus sales growth, in percentage points.
* **Format:** Decimal number, 2 dp
* **Expected:** Table by Year: 2022 −0.43 · 2023 −1.69 · 2024 **−13.32**.
* **Validate:** Table 2 by Year.

#### F22. Sales YTD
```dax
Sales YTD = TOTALYTD ( [Total Sales], DimDate[Date] )
```
* **Purpose:** Running total from 1 January.
* **Format:** Currency, 2 dp
* **Expected:** Matrix rows `DimDate[Year]` → `DimDate[Month]`: 2024 Jun **432,839.63**; 2024 Dec 1,192,590.88 (= full year).
* **Validate:** Add a Matrix to the Validation page, expand 2024.

#### F23. Region Rank
```dax
Region Rank =
IF (
    ISINSCOPE ( DimGeography[Region] ),
    RANKX ( ALLSELECTED ( DimGeography[Region] ), [Total Sales], , DESC, DENSE )
)
```
* **Purpose:** Rank of each region by sales.
* **Format:** Whole number
* **Expected:** Table by Region, no filter: West 1 · East 2 · Central 3 · South 4; total row blank.
* **Validate:** Table 2 by Region.

#### F24. Top Region
```dax
Top Region =
VAR TopRow =
    TOPN ( 1, VALUES ( DimGeography[Region] ), [Total Sales], DESC )
RETURN
    CONCATENATEX ( TopRow, DimGeography[Region], ", " )
```
* **Purpose:** Region with the highest sales in the selection.
* **Format:** Text
* **Expected:** No filter: **West**. Year 2024: West.
* **Validate:** Put it in a Card on the Validation page.

#### F25. Top Category
```dax
Top Category =
VAR TopRow =
    TOPN ( 1, VALUES ( DimProduct[Category] ), [Total Sales], DESC )
RETURN
    CONCATENATEX ( TopRow, DimProduct[Category], ", " )
```
* **Purpose:** Category with the highest sales in the selection.
* **Format:** Text
* **Expected:** No filter: **Technology**. Year 2024: Technology.
* **Validate:** Card.

#### F26. Loss-Making Lines
```dax
Loss-Making Lines =
CALCULATE ( COUNTROWS ( FactSales ), FactSales[Profit] < 0 )
```
* **Purpose:** Order lines with negative profit.
* **Format:** Whole number
* **Expected:** No filter: **1,907**.
* **Validate:** Validation table 1.

#### F27. Loss Line %
```dax
Loss Line % = DIVIDE ( [Loss-Making Lines], [Order Lines] )
```
* **Purpose:** Share of lines that lose money.
* **Format:** Percentage, 2 dp
* **Expected:** No filter: **16.64%**. Year 2024: 16.95%.
* **Validate:** Validation tables.

#### F28. Deep Discount Profit
```dax
Deep Discount Profit =
CALCULATE ( [Total Profit], FactSales[Discount] >= 0.3 )
```
* **Purpose:** Profit on lines with discount ≥ 30%.
* **Format:** Currency, 2 dp
* **Expected:** No filter: **−249,356.36**. Central: −96,101.03. Year 2024: −81,467.69.
* **Validate:** Validation tables by Region / Year.

#### F29. Max Uplift (Cap 20%)
```dax
Max Uplift (Cap 20%) =
SUMX (
    FILTER ( FactSales, FactSales[Discount] > 0.2 ),
    FactSales[Gross Sales] * ( FactSales[Discount] - 0.2 )
)
```
* **Purpose:** Upper-bound profit gain if discounts above 20% were 20% (same volume).
* **Format:** Currency, 2 dp
* **Expected:** No filter: **264,266.66**. Central 102,178.76 · West 71,258.06 · East 48,015.61 · South 42,814.23. Year 2024: 83,691.16.
* **Validate:** Validation tables by Region / Year.

#### F30. High Sales Low Margin
```dax
High Sales Low Margin =
VAR ProductCount = COUNTROWS ( ALLSELECTED ( DimProduct[Product Name] ) )
VAR SalesRank =
    RANKX ( ALLSELECTED ( DimProduct[Product Name] ), [Total Sales], , DESC )
RETURN
    IF (
        ISINSCOPE ( DimProduct[Product Name] ),
        IF ( SalesRank <= ProductCount * 0.25 && [Profit Margin %] < 0.05, 1, 0 )
    )
```
* **Purpose:** Flag = 1 for products in the top 25% by sales with margin < 5%.
* **Format:** Whole number
* **Expected:** Table of `DimProduct[Product Name]` filtered to flag = 1 (no slicers): **8 rows**: Round Table M702, Folding Work Table C380, Training Table D848, Rectangular Table R527, 3-Shelf Shelving Unit M597, Open Shelving Unit T373, Training Table W359, Orbit Smartphone L502.
* **Validate:** Validation page: Table with Product Name + this measure; visual filter `High Sales Low Margin is 1`.

#### F31. Margin Color
```dax
Margin Color =
SWITCH (
    TRUE (),
    [Profit Margin %] < 0, "#D03B3B",
    [Profit Margin %] < [Company Margin], "#EC835A",
    "#2A78D6"
)
```
* **Purpose:** Hex colour for conditional formatting.
* **Format:** Text
* **Expected:** Table by Region (no filter): Central and South `#EC835A` (below 10.29%), East and West `#2A78D6`. By Sub-Category: Tables, Bookcases, Supplies `#D03B3B`.
* **Validate:** Table 2 by Region; then by Sub-Category.


---

## PART G: Dashboard pages

### G0. Things that apply to every page

**Visual target for each page:** [mockups/](mockups/) contains a Python-rendered **design mockup** of every page, built from the same data. Use it as a picture of what you're aiming for: same visuals, same numbers. It is not a Power BI screenshot, so fonts and spacing in Power BI will look different.

**Visual wells vocabulary.** When you select a visual, the *Build* tab (*Visualizations → Build visual*) shows its *wells*: the boxes you drag fields into.

| What this guide calls | Bar chart | Line chart | Column chart | Card | Table | Matrix | Scatter | Filled map |
|---|---|---|---|---|---|---|---|---|
| **Axis** (categories) | Y-axis | X-axis | X-axis | – | Columns | Rows / Columns | Values (= one dot per item) | Location |
| **Values** (numbers) | X-axis | Y-axis | Y-axis | Fields / Data | Columns | Values | X Axis, Y Axis | Tooltips |
| **Legend** (series) | Legend | Legend | Legend | – | – | – | Legend | Legend |

**Always drag measures from `_Measures`**, never the raw column (e.g. `[Total Sales]`, not `FactSales[Sales]`).

**Canvas setup (once per page):** click empty canvas → *Format* pane → *Canvas settings → Type: 16:9*; *Canvas background → Color #FCFCFB, Transparency 0%*. *View → Page view → Fit to page*.

**Colours (meaning, not decoration):** single-series bars `#2A78D6` (blue). Red `#D03B3B` only for losses, via the `Margin Color` rule. Region series (line charts only): Central `#2A78D6`, East `#EB6834`, South `#1BAF7A`, West `#EDA100`.

**Titles:** select visual → *Format → General → Title → Text*. Use the title text given for each visual.

**Applying `Margin Color` to bars:** select the bar chart → *Format → Visual → Bars → Colors → fx* → *Format style: Field value* → *What field should we base this on?* `Margin Color` → OK.

### G1. Create the pages
Click **+** at the bottom to add pages; double-click a tab to rename. Final tab order:
1. `Executive Overview` · 2. `Regional Performance` · 3. `Product Performance` · 4. `Customer Performance` · 5. `Profitability & Discount` · `Region Detail` (hidden) · `Validation` (hidden at the end)

### G2. Slicers (create on page 1, then sync)
On **Executive Overview**, along the right edge, insert four slicers (*Visualizations → Slicer*):

| Slicer | Field well | Style (*Format → Visual → Slicer settings*) | Selection |
|---|---|---|---|
| Year | `DimDate[Year]` | Tile | Single select **Off**; "Select all" Off |
| Region | `DimGeography[Region]` | Dropdown | Multi-select with Ctrl |
| Category | `DimProduct[Category]` | Dropdown | Multi-select with Ctrl |
| Segment | `DimCustomer[Segment]` | Dropdown | Multi-select with Ctrl |

**Sync to all pages:** *View → Sync slicers* (a pane opens). Select each slicer in turn and tick **both** columns (⟳ sync, 👁 visible) for the five report pages. **Leave `Validation` and `Region Detail` unticked.**
**Why:** a manager picks a region once and every page follows. The Validation page stays unfiltered.
**Year behaviour:** click **2024** → everything shows 2024, and YoY cards show growth vs 2023. Clear the slicer (eraser icon on hover) → all four years; YoY cards show **blank**, which is correct, because YoY needs exactly one year.

### G3. Page 1: Executive Overview
**Question:** *Are we growing, and is the growth profitable?* **Set the Year slicer to 2024.**

**Layout (left to right, top to bottom):** six cards in a row → two trend lines → two bar charts → a key-messages text box. Slicers on the right.

| # | Visual (*Visualizations* icon) | Axis | Values | Legend | Formatting | Title |
|---|---|---|---|---|---|---|
| 1 | **Card** (or *Card (new)*) | – | `[Total Sales]` | – | Display units: Millions, 2 decimals. *Card (new):* *Reference labels → Add* → `[YoY Sales Growth %]` | Sales |
| 2 | Card | – | `[Total Profit]` | – | Thousands, 2 decimals; reference label `[YoY Profit Growth %]`; callout colour *fx → Rules*: < 0 → `#D03B3B` | Profit |
| 3 | Card | – | `[Profit Margin %]` | – | reference label `[Profit Margin PY]` | Profit margin (vs last year) |
| 4 | Card | – | `[Total Orders]` | – | Display units: None | Orders |
| 5 | Card | – | `[Total Quantity]` | – | None | Units sold |
| 6 | Card | – | `[Growth Gap (pp)]` | – | 2 decimals; *fx → Rules*: < 0 → red | Profit growth minus sales growth (pp) |
| 7 | **Line chart** | X-axis `DimDate[Year-Month]` | Y-axis `[Total Sales]` | – | *X-axis → Type: Categorical*; line colour `#2A78D6` | Monthly sales, 2021–2024 |
| 8 | Line chart | X-axis `DimDate[Year-Month]` | Y-axis `[Total Profit]` | – | as above | Monthly profit, 2021–2024 |
| 9 | **Clustered bar chart** | Y-axis `DimGeography[Region]` | X-axis `[Total Sales]`; Tooltips `[Profit Margin %]` | – | Bar colour = `Margin Color` (G0); data labels On | Sales by region (colour = margin vs company) |
| 10 | Clustered bar chart | Y-axis `DimProduct[Category]` | X-axis `[Total Profit]` | – | Bar colour = `Margin Color`; data labels On | Profit by category |
| 11 | **Text box** (*Insert → Text box*) | – | – | – | 11 pt | Key messages (text below) |

**Sorting:** bar charts → hover → **⋯** → *Sort axis → Total Sales* (or *Total Profit*) → *Sort descending*.
**Interactions:** select the **Year slicer** → *Format* ribbon → **Edit interactions** → on visuals 7 and 8 click **None** (⊘). The trends then always show all four years. Leave everything else on *Filter*. Click *Edit interactions* again to finish.
**Key-messages text (type it):**
* Sales grew 6.7% in 2024, but profit fell 6.6%. Growth came with deeper discounts (effective discount 15.6% → 16.2%).
* Central made a loss in 2024 (−$744) on $204K of sales.
* Furniture lost $6.1K in 2024, driven by Tables.

**You should see (Year = 2024):** Sales 1.19M (+6.69%) · Profit 110.24K (−6.63%, red) · Margin 9.24% (PY 10.56%) · Orders 1,393 · Units 15,341 · Gap −13.32 · Category profit: Technology 66,402.91, Office Supplies 49,894.89, Furniture −6,056.04 (red).

### G4. Page 2: Regional Performance
**Question:** *Which regions perform well, and which have profitability problems?*

| # | Visual | Axis | Values | Legend | Formatting | Title |
|---|---|---|---|---|---|---|
| 1 | **Table** | `DimGeography[Region]` (first column) | `[Total Sales]`, `[Sales Share %]`, `[YoY Sales Growth %]`, `[Total Profit]`, `[Profit Margin %]`, `[Margin vs Company]`, `[Effective Discount %]`, `[Region Rank]` | – | *Cell elements →* `Margin vs Company` *Background color → fx → Rules*: < 0 → light red `#F4C7C3`; `YoY Sales Growth %` *Font color* < 0 → red | Regional scorecard |
| 2 | Clustered bar chart | Y-axis `DimGeography[Region]` | X-axis `[Profit Margin %]` | – | Colour = `Margin Color`; *Analytics* (magnifier icon) *→ Constant line → Add → Value fx → `Company Margin`* | Profit margin by region (line = company) |
| 3 | Clustered bar chart | Y-axis `DimGeography[Region]` | X-axis `[Effective Discount %]` | – | colour `#2A78D6` | Share of list price given away as discount |
| 4 | **Line chart** | X-axis `DimDate[Year]` | Y-axis `[Total Sales]` | `DimGeography[Region]` | *X-axis Type: Categorical*; series colours as G0 | Yearly sales by region |
| 5 | **Filled map** (or *Azure Map*) | Location `DimGeography[State Location]` | Tooltips `[Profit Margin %]`, `[Total Sales]` | – | *Fill colors → fx → Gradient* on `[Profit Margin %]`, add a middle colour: min red, 0 white, max blue | Profit margin by state |

**Sorting:** table → click the `Total Sales` column header. Bar charts → descending.
**Interactions:** Year slicer → *Edit interactions* → visual 4 → **None**.
**Drill-through:** created in G9.
**You should see:**
* Year **cleared**: margin East 13.23%, West 12.27%, South 10.00%, Central 3.28%; effective discount Central 21.51%; Margin vs Company Central −7.01.
* Year **2024**: YoY East +25.76%, West +12.07%, Central −12.05%, South −12.18%; Central margin −0.37%.

*If maps are disabled* (*File → Options → Security → Map and Filled Map visuals*) and you can't enable them, skip visual 5. The scorecard answers the same question.

### G5. Page 3: Product Performance
**Question:** *Which products are destroying profit?* **Clear the Year slicer** to compare with the values below.

| # | Visual | Axis | Values | Legend | Formatting | Title |
|---|---|---|---|---|---|---|
| 1 | **Table** | `DimProduct[Category]` | `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]` | – | *Cell elements → Total Profit → Font color → fx → Rules*: < 0 → `#D03B3B` | Category summary |
| 2 | Clustered bar chart | Y-axis `DimProduct[Sub-Category]` | X-axis `[Total Profit]` | – | Colour = `Margin Color`; sort **ascending** by Total Profit (losses at top) | Profit by sub-category (red = loss) |
| 3 | **Scatter chart** | Values `DimProduct[Product Name]` | X Axis `[Total Sales]`, Y Axis `[Total Profit]` | – | *Markers → Colors → fx → Rules* based on `High Sales Low Margin`: = 1 → `#D03B3B`, otherwise `#C3C2B7` | Product sales vs profit (red = top-25% sales, margin < 5%) |
| 4 | **Table** | `DimProduct[Product Name]`, `DimProduct[Sub-Category]` | `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Effective Discount %]` | – | *Filters pane → this visual →* drag `High Sales Low Margin` → *is* `1` → Apply | High sales, low margin: action list |
| 5 | Table | `DimProduct[Product Name]` | `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]` | – | *Filters → Product Name → Top N → Top 10 by Total Sales* | Top 10 products by sales |
| 6 | Table | `DimProduct[Product Name]` | `[Total Profit]`, `[Effective Discount %]` | – | *Filters → Product Name → Top N → **Bottom** 10 by Total Profit* | 10 biggest loss-makers |

**Interactions:** clicking a sub-category bar filters the scatter and tables (default: leave as is).
**You should see (Year cleared):** category profit Technology 252,948.63, Office Supplies 200,916.89, Furniture −1,797.48; Tables −91,521.11, Bookcases −30,446.26, Supplies −1,745.06; action list = **8 rows**; bottom product Round Table M702 −26,412.30.

### G6. Page 4: Customer Performance
**Question:** *Which customers and segments matter, and are they profitable?* **Year cleared.**

| # | Visual | Axis | Values | Legend | Formatting | Title |
|---|---|---|---|---|---|---|
| 1 | Card | – | `[Customers]` | – | None | Active customers |
| 2 | Card | – | `[Sales per Customer]` | – | 2 decimals | Sales per customer |
| 3 | Card | – | `[Average Order Value]` | – | 2 decimals | Average order value |
| 4 | Clustered bar chart | Y-axis `DimCustomer[Segment]` | X-axis `[Total Sales]` | – | `#2A78D6` | Sales by segment |
| 5 | Clustered bar chart | Y-axis `DimCustomer[Segment]` | X-axis `[Profit Margin %]` | – | `#2A78D6` | Margin by segment |
| 6 | Clustered bar chart | Y-axis `DimCustomer[Customer Name]` | X-axis `[Total Sales]` | – | *Filters → Customer Name → Top N 10 by Total Sales* | Top 10 customers |
| 7 | **Scatter chart** | Values `DimCustomer[Customer Name]` | X Axis `[Total Sales]`, Y Axis `[Profit Margin %]` | `DimCustomer[Segment]` | marker size small | Customers: size vs profitability |
| 8 | Table | `DimCustomer[Customer Name]`, `DimCustomer[Segment]` | `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Effective Discount %]`, `[Total Orders]` | – | sort by Total Sales desc | Customer detail |

**You should see (Year cleared):** 741 customers · Sales per customer 5,926.01 · AOV 846.08 · Segment sales Consumer 2,379,132.35, Corporate 1,176,807.57, Home Office 835,236.08 · margins Corporate 11.12%, Consumer 10.29%, Home Office 9.15% · top customer Grace Diaz 69,516.61. With Year = 2024: 544 customers.

### G7. Page 5: Profitability & Discount
**Question:** *Are discounts causing margin problems, and what should management investigate?* **Year cleared.**

| # | Visual | Axis | Values | Legend | Formatting | Title |
|---|---|---|---|---|---|---|
| 1 | Card | – | `[Deep Discount Profit]` | – | Thousands; callout red | Profit on lines with ≥30% discount |
| 2 | Card | – | `[Max Uplift (Cap 20%)]` | – | Thousands; *subtitle On:* "Upper bound: assumes the same quantity would still sell" | What-if: cap discounts at 20% |
| 3 | Card | – | `[Loss Line %]` | – | 2 decimals | Share of order lines that lose money |
| 4 | **Clustered column chart** | X-axis `FactSales[Discount]` | Y-axis `[Profit Margin %]` | – | *X-axis → Type: Categorical*; colour = `Margin Color` (*Columns → Colors → fx*); data labels On | Profit margin at each discount level |
| 5 | **Matrix** | Rows `DimProduct[Sub-Category]`, Columns `DimGeography[Region]` | Values `[Total Profit]` | – | *Cell elements → Background color On → fx → Gradient*, add middle colour: Lowest `#D03B3B`, Center **number 0** white, Highest `#1C5CAB` | Profit by sub-category and region |
| 6 | Table | `DimProduct[Product Name]`, `DimProduct[Sub-Category]` | `[Total Profit]`, `[Effective Discount %]` | – | *Filters → this visual → Total Profit → is less than 0*; sort ascending | Loss-making products |
| 7 | Text box | – | – | – | | Investigate next (text below) |

**Investigate-next text (type it):**
1. Central discount approvals: 28% of Central's lines carry 30%+ discounts, against about 13% elsewhere.
2. Tables pricing: Tables lose money even at 10–20% discounts. Review list price and supplier cost.
3. South volume: sales fell 12% a year while margin stayed ~10%. Investigate lost customers, not prices.

**You should see (Year cleared):** −249,356.36 · 264,266.66 · 16.64% · column margins 0 → 24.86%, 0.2 → 5.78%, 0.3 → −7.72%, 0.8 → −319.52% · matrix Central × Tables −32,951 (deepest red cell). With Year = 2024: −81,467.69 · 83,691.16 · 16.95%.

### G8. Tooltips
Select every bar chart on pages 1–3 → drag `[Profit Margin %]` and `[YoY Sales Growth %]` into its **Tooltips** well. Hovering a bar then shows margin and growth. (YoY shows only when one year is selected.)

### G9. Hidden page: Region Detail (drill-through)
1. Select the `Region Detail` page. With **no visual selected**, find **Drill through** at the bottom of the *Visualizations → Build* pane → drag `DimGeography[Region]` into *Add drill-through fields here*. Power BI adds a ← back button.
2. Add a **Table**: `DimGeography[State]`, `DimGeography[City]`, `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Effective Discount %]`. Title: "Region detail by state and city".
3. Add a **Table**: `DimProduct[Product Name]`, `[Total Profit]`, with *Filters → Product Name → Top N → Bottom 10 by Total Profit*. Title: "Biggest loss-making products in this region".
4. Right-click the page tab → **Hide page**.
5. **Test:** on *Regional Performance*, right-click the Central bar → *Drill through → Region Detail*.
**You should see:** only Central's states and cities; the table total shows a margin of 3.28% (Year cleared).

### G10. Finish
1. On `Validation`, confirm the table still matches [DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md) → right-click the tab → **Hide page**.
2. Set slicers: Year = 2024, others cleared. *View → Bookmarks → Add* → rename `Default`.
3. On each page: *Insert → Buttons → Reset* → *Format → Action → Type: Bookmark → Default* (title "Reset filters"). Optionally *Insert → Buttons → Navigator → Page navigator*.
4. Add a small text box, bottom right of every page: "Synthetic RetailCo data, 2021–2024. Sales = revenue after discount."
5. **Save** (Ctrl + S).
6. Run [FINAL_VALIDATION.md](FINAL_VALIDATION.md) (Levels 1–4). Its last two sections cover the screenshots and committing the `.pbix` to GitHub.
