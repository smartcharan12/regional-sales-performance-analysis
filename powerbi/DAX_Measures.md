# DAX Measures

> ⚠️ **Power BI Desktop validation required:** this DAX has not yet been executed in Power BI. See Part 8.

All measures reference the star schema described in [Data_Model.md](Data_Model.md):
`FactSales`, `DimDate`, `DimCustomer`, `DimProduct`, `DimGeography`.

**Tip:** create an empty table called `_Measures` (*Enter data → OK*) and store every measure in it, so they are easy to find.

---

## Part 1 — DAX from zero

### What is DAX?
**DAX (Data Analysis Expressions)** is the formula language of Power BI. It looks a little like Excel formulas, but it works on **whole tables and columns**, not on individual cells.

### Why do we need it?
A chart in Power BI can only show what the model can calculate. "Total Sales" is easy (just add up a column), but "Profit Margin for the selected region, compared with the same period last year" needs logic. DAX supplies that logic, and recalculates it automatically every time a user clicks a slicer.

### The most important idea: *filter context*
Every number on a report is calculated **inside a set of filters**: the slicers, the row of a table, the bar of a chart.

> The measure `Total Sales = SUM(FactSales[Sales])` is written **once**. In the bar for "West" it returns West's sales; in the card at the top it returns the company total; with the slicer set to 2024 it returns 2024 only. The formula never changes — the **filter context** does.

### Calculated column vs measure vs Power Query

| | Calculated column | Measure | Power Query column |
|---|---|---|---|
| Computed | Once per row, at refresh | On the fly, for each visual/filter | Once per row, at refresh (before the model) |
| Stored in the file | Yes (uses memory) | No (just the formula) | Yes |
| Reacts to slicers | No (fixed value per row) | **Yes** | No |
| Typical use | A row-level attribute to slice by, e.g. a price band | Totals, ratios, YoY, rankings | Data types, cleaning, merging, a fixed category |
| Example here | *(not needed: Python created `Discount Band`)* | `[Profit Margin %]` | Setting `Order Date` to Date type |

**Why Profit Margin must be a measure:** a calculated column would compute margin per row. Summing or averaging those row margins gives the wrong answer (notebook 02 shows the error: 11.7% vs the true 10.3%). A measure computes `SUM(Profit) / SUM(Sales)` **for whatever is selected**, which is always correct.

### Three functions you will see everywhere

| Function | What it does |
|---|---|
| `DIVIDE(a, b)` | a ÷ b, but returns BLANK instead of an error when b = 0 |
| `CALCULATE(expression, filters…)` | Evaluates an expression **after changing the filter context**. The most important DAX function |
| `VAR … RETURN` | Stores an intermediate result under a name. Makes formulas readable and avoids calculating the same thing twice |

---

## Part 2 — Base measures

### Total Sales
```dax
Total Sales = SUM ( FactSales[Sales] )
```
* **Logic:** adds up the `Sales` column for all rows visible in the current filter context.
* **Returns:** revenue after discount, in $.
* **Changes when:** any slicer or visual filter touches FactSales or a related dimension.
* **Expected (no filters):** **$4,391,176.00**

### Total Profit
```dax
Total Profit = SUM ( FactSales[Profit] )
```
* Profit after cost of goods; can be negative for a selection (e.g. Tables). **Expected:** **$452,068.04**

### Total Quantity
```dax
Total Quantity = SUM ( FactSales[Quantity] )
```
* Units sold. **Expected:** **56,703**. *Limitation:* adds pens and copiers together, so use it for logistics, not value.

### Total Orders
```dax
Total Orders = DISTINCTCOUNT ( FactSales[Order ID] )
```
* **Logic:** counts *unique* order IDs. `COUNTROWS` would count order **lines** (11,461) instead of orders.
* **Expected:** **5,190**

### Order Lines
```dax
Order Lines = COUNTROWS ( FactSales )
```

### Customers
```dax
Customers = DISTINCTCOUNT ( FactSales[Customer ID] )
```
* Counts customers who **bought in the current selection** (741 overall).

---

## Part 3 — Ratio measures

### Profit Margin %
```dax
Profit Margin % =
DIVIDE ( [Total Profit], [Total Sales] )
```
* **Line by line:** take the profit of the current selection, divide by its sales. `DIVIDE` protects against an empty selection.
* **Format:** *Measure tools → Format → Percentage, 1 decimal*.
* **Returns:** 10.3% overall; East 13.2%, Central 3.3%.
* **Slicers:** recalculated from the *totals* of the selection, so it is always correctly weighted.

### Average Order Value
```dax
Average Order Value =
DIVIDE ( [Total Sales], [Total Orders] )
```
* Revenue per order (**$846.08** overall). Uses orders, not lines.

### Sales per Customer
```dax
Sales per Customer = DIVIDE ( [Total Sales], [Customers] )
```
* Average revenue per active customer in the selection (**$5,926.01** overall).

### Gross Sales, Discount Amount, Effective Discount %
```dax
Gross Sales     = SUM ( FactSales[Gross Sales] )
Discount Amount = SUM ( FactSales[Discount Amount] )

Effective Discount % =
DIVIDE ( [Discount Amount], [Gross Sales] )
```
* **Why not `AVERAGE(FactSales[Discount])`?** A simple average treats a 50% discount on a $3 pen the same as a 50% discount on a $3,000 copier. Effective discount weights by money. **Expected:** 15.5% overall; Central 21.5%.

### Sales Share %
```dax
Sales Share % =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALLSELECTED ( DimGeography[Region] ) )
)
```
* **Logic:** the denominator removes the *Region* filter coming from the visual (so each bar is compared with the total of all regions), but `ALLSELECTED` still respects the slicers the user chose (e.g. Year = 2024).
* **Returns:** West ≈ 34.45% (all years).

### Company Margin (the benchmark)
```dax
Company Margin =
CALCULATE (
    [Profit Margin %],
    REMOVEFILTERS ( DimGeography ),
    REMOVEFILTERS ( DimProduct ),
    REMOVEFILTERS ( DimCustomer )
)
```
* **Logic:** the margin of the **whole company** for the **dates currently selected**. Region, product and customer filters are removed; date filters (the Year slicer) are kept.
* **Expected:** 10.29% (all years); 9.24% with Year = 2024.
* **Why one benchmark:** every "above/below company" comparison in the report (reference line, colours, `Margin vs Company`) uses this same measure, so they can never disagree.

### Margin vs Company (pp)
```dax
Margin vs Company = ( [Profit Margin %] - [Company Margin] ) * 100
```
* Format as *Decimal number*, 2 decimals (it is already in percentage points, so don't apply % format).
* Difference, in percentage points, between the current selection's margin and the company margin for the same dates. Negative = below the company. **Expected:** Central −7.01 pp, East +2.94 pp, West +1.97 pp, South −0.30 pp (all years).

---

## Part 4 — Time intelligence

Time intelligence = comparing a period with another period (last year, year-to-date). It **requires** `DimDate` to be a complete calendar marked as a date table (see Data_Model.md).

### Sales PY (previous year)
```dax
Sales PY =
CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
```
* **Line by line:** `SAMEPERIODLASTYEAR` takes the dates currently in the filter (e.g. all of 2024) and shifts them back one year (all of 2023). `CALCULATE` then evaluates `[Total Sales]` on those shifted dates.
* **Returns:** with Year = 2024 selected → **$1,117,829.65** (2023's sales).
* **Changes when:** the date selection changes. Other slicers (Region…) are kept, so "Central PY" works automatically.

### YoY Sales Growth %
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
* **Line by line:** store this period's sales and last year's sales in variables. Return (current − previous) ÷ previous **only if exactly one year is in context and a previous year exists**; otherwise BLANK.
* **Why `HASONEVALUE`?** With no year selected, the context is all of 2021–2024, and `SAMEPERIODLASTYEAR` would compare it with 2020–2023 (where 2020 has no data). That gives a large, meaningless "growth". The guard makes the card show BLANK until a single year is chosen, and it still works per month in a line chart (each month belongs to one year). It also hides 2021, which has no previous year.
* **Expected:** 2024 → **+6.7%**, 2023 → +8.0%.

### Profit PY and YoY Profit Growth %
```dax
Profit PY =
CALCULATE ( [Total Profit], SAMEPERIODLASTYEAR ( DimDate[Date] ) )

YoY Profit Growth % =
VAR CurrentProfit = [Total Profit]
VAR PreviousProfit = [Profit PY]
RETURN
    IF (
        HASONEVALUE ( DimDate[Year] ) && NOT ISBLANK ( PreviousProfit ),
        DIVIDE ( CurrentProfit - PreviousProfit, ABS ( PreviousProfit ) )
    )
```
* **Why `ABS`?** If last year's profit was negative, dividing by it flips the sign. Example: a loss of −$1,000 last year improving to a profit of +$500 is (500 − (−1,000)) ÷ (−1,000) = **−150%** without `ABS` (looks like a collapse), but **+150%** with `ABS` (correct direction). In this data Central's profit turns negative in 2024, so this would matter as soon as 2025 data arrives.
* **Expected:** 2024 → **−6.6%**. *Limitation:* growth % is unstable when the previous value is close to zero, so show the $ change next to it.

### Profit Margin PY
```dax
Profit Margin PY = DIVIDE ( [Profit PY], [Sales PY] )
```
* Last year's margin for the same selection, used as the reference label on the margin card. **Expected:** Year = 2024 → **10.56%** (2023's margin).

### Growth Gap (pp): detects "sales up, profit down"
```dax
Growth Gap (pp) = ( [YoY Profit Growth %] - [YoY Sales Growth %] ) * 100
```
* Negative = profit growing slower than sales (margin erosion). 2024: (−6.63% − 6.69%) × 100 = **−13.32 pp**. Format as *Decimal number*. A red value here is an early warning that sales growth is being bought with discounts.

### Sales YTD
```dax
Sales YTD = TOTALYTD ( [Total Sales], DimDate[Date] )
```
* Running total from 1 January to the latest date in the current context. Used in the monthly trend tooltip.

---

## Part 5 — Ranking & "Top" measures

### Region Rank (by sales)
```dax
Region Rank =
IF (
    ISINSCOPE ( DimGeography[Region] ),
    RANKX ( ALLSELECTED ( DimGeography[Region] ), [Total Sales], , DESC, DENSE )
)
```
* **Logic:** `ISINSCOPE` makes sure the rank only appears on region rows (not on the total row). `RANKX` evaluates `[Total Sales]` for every region in the selection and returns this region's position.

### Top Region / Top Category (for KPI cards)
```dax
Top Region =
VAR TopRow =
    TOPN ( 1, VALUES ( DimGeography[Region] ), [Total Sales], DESC )
RETURN
    CONCATENATEX ( TopRow, DimGeography[Region], ", " )

Top Category =
VAR TopRow =
    TOPN ( 1, VALUES ( DimProduct[Category] ), [Total Sales], DESC )
RETURN
    CONCATENATEX ( TopRow, DimProduct[Category], ", " )
```
* `TOPN(1, …)` returns the row(s) with the highest sales among the regions visible under the current slicers. `CONCATENATEX` turns that table into text for a card (it would list both names if two were tied).
* **Expected:** West · Technology.

---

## Part 6 — Profitability & discount measures

### Loss-Making Lines and Loss Line %
```dax
Loss-Making Lines =
CALCULATE ( COUNTROWS ( FactSales ), FactSales[Profit] < 0 )

Loss Line % = DIVIDE ( [Loss-Making Lines], [Order Lines] )
```
* **Expected:** 1,907 lines, **16.6%**.

### Profit on Deep Discounts (≥ 30%)
```dax
Deep Discount Profit =
CALCULATE ( [Total Profit], FactSales[Discount] >= 0.3 )
```
* **Expected:** **−$249,356**. Shows how much money the 30%+ discount lines lose in the current selection.

### Max Uplift if Discount Capped at 20% (what-if, upper bound)
```dax
Max Uplift (Cap 20%) =
SUMX (
    FILTER ( FactSales, FactSales[Discount] > 0.2 ),
    FactSales[Gross Sales] * ( FactSales[Discount] - 0.2 )
)
```
* **Logic:** `SUMX` iterates row by row. For every line discounted above 20%, it adds back the extra price that would have been charged at 20%. Cost doesn't change, so this is also the extra profit.
* **Expected:** ≈ **$264,267**. ⚠️ Assumes the same quantity would still sell. Label the visual "upper bound".

### High Sales / Low Margin flag (for product tables)
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
* Returns 1 for products in the top 25% by sales with a margin below 5%. Use it as a visual-level filter (`is 1`) or for conditional formatting. **Expected:** 8 products.

### Margin colour (conditional formatting)
```dax
Margin Color =
SWITCH (
    TRUE (),
    [Profit Margin %] < 0, "#D03B3B",
    [Profit Margin %] < [Company Margin], "#EC835A",
    "#2A78D6"
)
```
* Red `#D03B3B` = loss; orange `#EC835A` = below company margin; blue `#2A78D6` = healthy. Uses `[Company Margin]` from Part 3.
* Apply via *Format visual → Bars/Columns → fx → Field value → Margin Color*.

---

## Part 7 — How slicers affect the measures (summary)

| Slicer selected | `Total Sales` | `Profit Margin %` | `Sales PY` | `Sales Share %` | `Company Margin` |
|---|---|---|---|---|---|
| Year = 2024 | 2024 only | 2024 only | 2023 | Share within 2024 | 2024 company margin |
| Region = Central | Central only | Central only | Central last year | 100% (only one region left) | **Ignores** region → company figure |
| Category = Furniture | Furniture only | Furniture only | Furniture last year | Share of Furniture sales by region | **Ignores** product → all products |
| *No Year selected* | all years | all years | shifted range (not meaningful) | all years | all years. YoY measures show BLANK by design |

## Part 8 — Validation

Every measure above has an expected value, a test procedure and a common mistake in **[DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md)**. Tick it off in Power BI Desktop as you build.

> ⚠️ **Power BI Desktop validation required.** These measures were written against the exact table and column names in `data/processed/powerbi/*.csv`, and their expected values were computed in Python and confirmed in MySQL. The DAX itself has **not** been run (Power BI Desktop is not available on Linux).
