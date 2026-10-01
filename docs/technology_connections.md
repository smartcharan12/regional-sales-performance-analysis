# How the Technologies Fit Together

This project uses Python, SQL, Power BI and DAX. They are **not four separate skills bolted together**. Each does the job it is best at, and each hands its output to the next.

```
            ┌───────────── Python ─────────────┐
 Raw CSV ──►│ clean · validate · test · EDA    │──► clean CSV + star-schema CSVs
            └──────────────────────────────────┘              │
                                     ┌────────────────────────┴───────────────┐
                                     ▼                                        ▼
                         ┌──────── SQL (MySQL) ───────┐        ┌──── Power BI ─────────────┐
                         │ store · join · aggregate    │        │ Power Query: load & type  │
                         │ verify the numbers          │        │ Model: star schema        │
                         └─────────────────────────────┘        │ DAX: dynamic measures     │
                                                                │ Visuals: dashboard        │
                                                                └───────────────────────────┘
```

## Why Python?
**Used for:** cleaning, validation, exploratory analysis, statistics, automation, testing.

* Cleaning needs **logic** ("if Region is missing, look it up from State; if Discount > 1 and ÷100 gives a valid level, fix it"). That logic is easy to write, read and **unit-test** in Python.
* EDA needs fast iteration: one line of pandas → a new grouping; one function → a new chart.
* The pipeline is **reproducible**: `python src/pipeline.py` rebuilds everything from raw data.
* Statistics (correlation, distributions, IQR outliers) are built in.

**Not used for:** the business-facing dashboard. A static PNG can't be filtered by a regional manager.

## Why SQL?
**Used for:** storing the data, extraction, filtering, joining, aggregation, verification.

* In a real company the data lives in a **database**, not a CSV. SQL is how an analyst gets to it.
* The star schema in MySQL enforces rules **in the database itself**: primary keys, foreign keys and `CHECK (sales > 0)`.
* SQL is an **independent check**: the same totals computed by a different engine prove the Python numbers right. (Validated: identical totals to the cent.)
* `data_quality.sql` shows that the raw data can be profiled without any Python.

## Why Power BI?
**Used for:** interactive reporting, slicers, KPI monitoring, stakeholder communication, sharing.

* Managers don't run notebooks. They need to **click** a region or a year and see the answer.
* One model serves five audiences (CEO, regional managers, finance, …) through pages, slicers and row-level security.
* Refreshable: point it at the database and the dashboard updates every day with no analyst involved.

## Why DAX?
**Used for:** dynamic business calculations, time intelligence, measures.

* A margin must be recalculated for **whatever the user selects**. That is exactly what a DAX measure does.
* Time intelligence (`SAMEPERIODLASTYEAR`, `TOTALYTD`) gives YoY and YTD for any selection with one formula.
* Python could compute "Central's 2024 margin", but only for the combinations you thought of in advance. DAX computes every combination on demand.

## Power Query vs DAX vs Python: when to use which

| Task | Best tool | Why |
|---|---|---|
| Complex cleaning with rules and tests | **Python** | Testable, version-controlled, reusable |
| Statistical exploration, one-off analysis | **Python** | Flexible, fast iteration |
| Pulling and joining data from a database | **SQL** | Runs where the data lives; efficient |
| Setting data types, renaming, simple merges inside the report | **Power Query** | Repeats automatically on refresh, no code outside Power BI |
| A ratio/total that must react to slicers | **DAX measure** | Only DAX is evaluated in the filter context |
| A fixed attribute to slice by (e.g. Discount Band) | Python / Power Query (upstream) | Computed once, cheaper than a calculated column |

**Guiding rule:** *transform data as far upstream as possible; calculate as late as necessary.* Static shaping belongs upstream (Python/SQL/Power Query). Anything that depends on the user's selection belongs in DAX.

## A single question through all four tools

> *"What was Central's profit margin in 2024, and how does it compare with last year?"*

1. **Python** ensured that every Central row is labelled "Central" (35 regions rebuilt from State, variants like `Centrl` fixed) and that discounts are fractions. Without this, the answer would be wrong before any calculation.
2. **SQL** confirms it: `SUM(profit)/SUM(sales)` grouped by region and year on `v_sales` → −0.4% in 2024 vs 3.3% in 2023.
3. **Power BI / Power Query** loads the star schema with correct types and relationships.
4. **DAX** `[Profit Margin %]` with slicers Region = Central, Year = 2024 → −0.4%; `[Profit PY]` gives 2023 automatically.
