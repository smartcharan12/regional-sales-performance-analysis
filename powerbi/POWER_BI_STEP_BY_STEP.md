# Power BI Concepts for Beginners

> **To build the dashboard, follow [POWER_BI_MASTER_GUIDE.md](POWER_BI_MASTER_GUIDE.md).** It is the single click-by-click guide.
> This page keeps the **concept explanations** a beginner needs while building: what Power BI is, why we use a star schema, how Power Query, relationships and filter context work, and calculated columns vs measures. It was previously a full step-by-step guide; its procedural steps were merged into the Master Guide so that there is only one set of instructions to follow.

| You want to… | Go to |
|---|---|
| Import the CSVs, set the data types | [Master Guide Part B–C](POWER_BI_MASTER_GUIDE.md#part-b-create-the-power-bi-project) |
| Create relationships, mark the date table | [Part D–E](POWER_BI_MASTER_GUIDE.md#part-d-relationships) |
| Create and validate the 31 measures | [Part F](POWER_BI_MASTER_GUIDE.md#part-f-dax-measures-all-31-in-build-order), [DAX_VALIDATION_CHECKLIST.md](DAX_VALIDATION_CHECKLIST.md) |
| Build the 5 pages, slicers, drill-through, tooltips | [Part G](POWER_BI_MASTER_GUIDE.md#part-g-dashboard-pages) |
| Fix an error | [POWER_BI_TROUBLESHOOTING.md](POWER_BI_TROUBLESHOOTING.md) |
| Prove the dashboard is correct; screenshots; publishing | [FINAL_VALIDATION.md](FINAL_VALIDATION.md) |

## 1. What Power BI is

Power BI Desktop is a free Microsoft program for building **interactive reports**. You load data, connect the tables, write formulas, and drag charts onto pages. A manager can then click "Central" or "2024" and every chart updates instantly.

It has three main views, shown as icons on the **left edge** of the window:

| Icon | View | Used for |
|---|---|---|
| 📊 bar chart | **Report view** | Designing pages and charts |
| ▦ table grid | **Table view** (older versions: *Data view*) | Looking at the rows of a table |
| ⧉ connected boxes | **Model view** | Connecting tables (relationships) |

Plus a separate window, the **Power Query Editor**, for preparing data before it loads.

## 2. Why this project uses Power BI

The Python notebooks answer questions **we** thought of. A regional manager will have their own questions: "only my region", "only 2024", "only Furniture". Power BI lets them ask these by clicking, without code. It is also the most common BI tool in analyst job descriptions, so building it properly is a core part of the project.

| Python already did | Power BI adds |
|---|---|
| Cleaning, validation, testing | Interactivity (slicers, cross-filtering) |
| Static charts for the analysis | A reusable report for non-technical people |
| One-time answers | Answers to *any* combination of filters, through measures |

## 3. Why FactSales plus "dimensions"?

Imagine one giant spreadsheet in which every sale repeats the customer's name, segment, the product's category, the city, the region… That is a **flat table**. It works, but it repeats a lot, and it makes some calculations (like "same period last year") awkward.

Instead we use a **star schema**:

```
            DimDate
               │
DimCustomer ── FactSales ── DimProduct
               │
          DimGeography
```

* **Fact table** (`FactSales`): *events* with numbers. Long: 11,461 rows.
* **Dimension tables** (`Dim…`): *descriptions* you filter and group by. Short: each customer, product, place or day appears **once**.
* Each dimension has a **key** (e.g. `Product ID`) that also appears in `FactSales`. Matching keys is how Power BI knows which product each sale belongs to.

When you click "Technology" in a slicer built on `DimProduct`, Power BI finds the Technology product IDs, follows the link to `FactSales`, keeps only those sales, and recalculates every number. That flow (**dimension → fact**) is the whole idea.

## 4. Power Query basics

The **Power Query Editor** is where you *prepare* tables before they enter the model. Every action you take is recorded as a step in **Applied Steps** (right side), and the steps re-run automatically on every refresh.

| Area | What it is |
|---|---|
| Queries (left) | One query per table |
| Preview (middle) | First rows of the selected query |
| Applied Steps (right) | The recipe. Click a step to see the data at that point; ✕ deletes a step |
| Column header icon (ABC / 123 / 📅) | The column's data type. Click it to change the type |

**Rule:** Power Query is for *shaping* (types, renaming, merging). Calculations that must react to clicks (totals, margins) are **not** done here; they're DAX measures ([Master Guide Part F](POWER_BI_MASTER_GUIDE.md#part-f-dax-measures-all-31-in-build-order)).

## 5. One-to-many explained

*One* product (one row in `DimProduct`) appears on *many* sales lines in `FactSales`. That is **one-to-many**. The "one" side must have unique keys, like a phone book where each name appears once. If it didn't, Power BI couldn't tell which description to use.

## 6. Filter direction explained

The arrow on each relationship line shows which way filters travel. **Single direction (dimension → fact)** means: choosing "Central" in `DimGeography` filters `FactSales`, but filtering `FactSales` doesn't reach back and filter other dimensions.

**Why single:** it's predictable and fast. "Both" directions can create two competing paths between tables (ambiguity) and slow the model. Every question in this report flows naturally from dimension to fact.
**Common mistake:** setting "Both" to make a slicer show only customers who bought something. → Use a visual-level filter or a measure filter instead.

## 7. Filter context: the one idea that makes DAX click

`Total Sales` is written **once**. In a table split by Region it shows four different numbers, and with the Year slicer on 2024 it shows 2024 only. The formula never changes; what changes is the **filter context**, meaning the set of filters active for that particular cell (slicers + the visual's row/column + page filters). Every measure in this report works this way.

## 8. Calculated column vs measure

| | Calculated column | Measure |
|---|---|---|
| Calculated | once per row, when data refreshes | at the moment a visual is drawn |
| Reacts to slicers? | **No** | **Yes** |
| Stored in the file | yes (uses memory) | no (just the formula) |
| Use for | something to slice/group by | totals, ratios, comparisons |

**Example of why it matters:** if you make a *column* `Profit / Sales` and then average it, the company margin comes out ≈ **11.74%**. The correct margin, from a *measure* `DIVIDE([Total Profit], [Total Sales])`, is **10.29%**. The average gives a $3 order the same weight as a $3,000 one. **Rule for this project:** every number on the dashboard is a measure.
