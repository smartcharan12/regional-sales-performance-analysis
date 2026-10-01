# START HERE: The Whole Project, From Zero

This guide assumes you know **nothing** about data analytics. Read it top to bottom once. After that, every other file in this repository will make sense.

---

## Part 1 · A tiny example first

Imagine a small shop that sells **laptops, phones and accessories** in four areas: **North, South, East and West**.

The manager asks one question:

> **"Which region is performing best?"**

What does an analyst actually do?

```
Sales data → Clean the data → Calculate sales → Compare regions
           → Visualise results → Find the reason → Recommend action
```

**1. Sales data.** Every sale is written down as one row:

| Date | Region | Product | Sales ($) | Profit ($) |
|---|---|---|---|---|
| 2024-01-03 | North | Laptop | 1,000 | 150 |
| 2024-01-03 | north | Phone | 500 | 100 |
| 2024-01-04 | South | Laptop | 1,000 | −50 |
| 2024-01-04 | South | Laptop | 1,000 | −50 |
| 2024-01-05 | East |  | 200 | 60 |

**2. Clean the data.** Look closely and you'll spot problems:
* `North` and `north` are the same region, written differently. The computer thinks they are two regions.
* The two South rows are identical. Was the same sale recorded twice? If so, counting both doubles South's sales.
* The East row has no product. Can we find out what it was? If not, can we still use the row? (Yes, for regional totals the product doesn't matter.)

**3. Calculate.** Add up sales and profit per region.

**4. Compare.** North: $1,500 sales, $250 profit. South: $1,000 sales (after removing the duplicate) and a **loss** of −$50.

**5. Visualise.** A bar chart of sales and profit by region makes the comparison obvious in two seconds.

**6. Find the reason.** Why does South lose money on laptops? Maybe it sells them at a big discount. We check the data.

**7. Recommend.** "Review laptop discounts in the South." This is something the manager can actually do.

**That is the entire project in miniature.** The real project does exactly these seven things, with 11,567 rows instead of 5, and with professional tools at each step.

---

## Part 2 · The vocabulary you need

| Term | Meaning |
|---|---|
| **Dataset** | A table of recorded facts |
| **Row / record** | One fact, e.g. one product on one order |
| **Column / field** | One property of every row, e.g. `Sales` |
| **Grain** | What exactly one row represents. Here it is one **order line** (one product inside one order) |
| **Categorical data** | Labels used for grouping: Region, Category |
| **Numerical data** | Quantities you can add up: Sales, Profit |
| **Datetime data** | Dates and times: Order Date |
| **Missing value** | An empty cell |
| **Duplicate** | A row that appears more than once |
| **Outlier** | A value far from the others. Not necessarily wrong! |
| **Aggregation** | Combining many rows into one number: SUM, AVERAGE, COUNT |
| **Sales (Revenue)** | Money received from customers after discount |
| **Profit** | Sales minus what the products cost us. Can be negative (a loss) |
| **Profit margin** | Profit ÷ Sales: how many cents of each dollar we keep |
| **Discount** | Price reduction. In this data 0.2 means 20% |
| **KPI** | Key Performance Indicator: a number management watches regularly |
| **YoY** | Year-over-Year: this year compared with last year |
| **EDA** | Exploratory Data Analysis: looking at data from many angles to find patterns |
| **Correlation** | How strongly two things move together (−1 to +1). **It does not prove that one causes the other** |
| **Data model** | How tables are connected to each other |
| **Fact table** | Table of events with numbers (each sale) |
| **Dimension table** | Table of descriptions (customers, products, dates, places) |
| **Star schema** | One fact table in the middle, dimension tables around it |
| **Dashboard** | An interactive screen of charts and numbers |
| **Slicer** | A filter button on a dashboard (e.g. choose Year = 2024) |
| **Measure (DAX)** | A Power BI formula that recalculates when you click a filter |

---

## Part 3 · The tools, and why each one is here

| Tool | One-line job | Analogy |
|---|---|---|
| **Python** | Cleans, checks and explores the data | The workshop where raw material is cleaned and inspected |
| **pandas** | Python's table library | A super-powered spreadsheet you control with code |
| **NumPy** | Fast maths for pandas | The calculator inside pandas |
| **Matplotlib / Seaborn** | Draw charts in Python | The analyst's sketchpad |
| **Jupyter Notebook** | Mixes code, results and explanation in one document | A lab notebook |
| **SQL / MySQL** | Stores data in a database and asks it questions | The warehouse plus its catalogue system |
| **Power BI** | Builds interactive dashboards for managers | The shop window |
| **Power Query** | Loads and shapes data inside Power BI | The loading dock |
| **DAX** | Formulas that power the dashboard numbers | The cash register that totals whatever you select |
| **Git / GitHub** | Saves versions and shares the project | The filing cabinet with history |

**Why not one tool for everything?** Each one is much better at its own job. Cleaning rules are easy to *test* in Python. Data in companies lives in *databases*, which you query with SQL. Managers need *clickable* dashboards, which is Power BI. And numbers that change when you click need *DAX*. [More detail →](docs/technology_connections.md)

---

## Part 4 · The real project, step by step

**The company:** RetailCo sells furniture, office supplies and technology in four US regions: West, East, Central and South.
**The problem:** sales went up in 2024, but profit went down. Nobody knows why.
[Full story →](docs/company_scenario.md)

### Step 1 · Get the data → `data/raw/sales_raw.csv`
11,567 rows, one per product sold. The data is **synthetic**: it was generated by `src/generate_data.py` from written-down business rules, and a known set of mistakes was added on purpose so that we have something real to clean. Read [`docs/data_dictionary.md`](docs/data_dictionary.md) to learn what each column means.

### Step 2 · Understand the data → [`notebooks/01_data_understanding.ipynb`](notebooks/01_data_understanding.ipynb)
We look before we touch. How many rows are there? What type is each column? What is missing? What is duplicated? **Output:** a list of 10 problems, each with a planned fix.

*Key lesson:* one order can contain several products, so `Order ID` repeating is **normal**. A row repeating *in every column* is a real duplicate.

### Step 3 · Clean the data → [`notebooks/02_data_cleaning.ipynb`](notebooks/02_data_cleaning.ipynb), [`src/data_cleaning.py`](src/data_cleaning.py)
**Fix before you delete.** A missing region is rebuilt from the state (Texas is always Central). A missing customer name is looked up from the customer ID. `"$1,277.10"` becomes the number 1277.10.
**Delete only what can't be trusted:** a sale with no amount, a quantity of −2, or a date like 30 February.
**Result:** 11,567 → 11,461 rows; 275 values repaired; every decision logged in `data/processed/cleaning_log.csv`.
**Proof:** `python tests/test_pipeline.py` checks the cleaned values against the original error-free data.

### Step 4 · Add helpful columns (feature engineering) → [`src/feature_engineering.py`](src/feature_engineering.py)
Year, Month, Profit Margin, Discount Amount and so on. This makes later questions one line of code.

*Key lesson:* **Profit margin** is fairer than profit for comparing regions. A big region always has more profit, simply because it is big. Margin asks "how much do you keep per dollar?"

### Step 5 · Explore (EDA) → [`notebooks/03_eda.ipynb`](notebooks/03_eda.ipynb), [`visualizations/`](visualizations/)
13 charts, each answering one question. Sales by region. Profit by region. Margin by region. Monthly trend. Products that sell a lot but lose money. Discount vs profit.

*Key lesson:* pick the chart for the question. **Comparing categories → bar. Change over time → line. Two numbers per item → scatter. A grid of two categories → heatmap.**

### Step 6 · Answer business questions & define KPIs → [`notebooks/04_business_analysis.ipynb`](notebooks/04_business_analysis.ipynb)
17 questions answered with numbers computed in the notebook, plus precise definitions of each KPI (Total Sales, Profit Margin, YoY Growth…). Two deep dives: why 2024 profit fell, and why Central's margin is so low.

### Step 7 · Store & check with SQL → [`sql/`](sql/)
The same data is loaded into a MySQL database and the same questions are asked in SQL. The totals match Python to the cent, which is an independent proof that the numbers are right. The SQL files go from basic (`SELECT`, `WHERE`) to advanced (CTEs, window functions), with comments on every query.

### Step 8 · Model the data → [`powerbi/Data_Model.md`](powerbi/Data_Model.md)
Split into a **star schema**: a `FactSales` table (the numbers) linked to `DimDate`, `DimCustomer`, `DimProduct` and `DimGeography` (the descriptions).

### Step 9 · Write the DAX measures → [`powerbi/DAX_Measures.md`](powerbi/DAX_Measures.md)
Formulas such as `Profit Margin % = DIVIDE([Total Profit], [Total Sales])`. Each is written once, and it gives the right answer for whatever region, year or product is selected.

### Step 10 · Build the dashboard → [`powerbi/POWER_BI_MASTER_GUIDE.md`](powerbi/POWER_BI_MASTER_GUIDE.md)
Five pages: Executive, Regional, Product, Customer, Profitability. [`Dashboard_Design.md`](powerbi/Dashboard_Design.md) lists every visual, its fields, why it was chosen, and the number it should show. **This step is done by you in Power BI Desktop (Windows)**: the repository contains the full specification and a click-by-click guide, but not a finished `.pbix` file.

### Step 11 · Insights & recommendations → [`reports/`](reports/)
* [`Business_Insights.md`](reports/Business_Insights.md): each insight is written as **fact → possible explanation → what to check → action**.
* [`Executive_Summary.md`](reports/Executive_Summary.md): the one page a CEO would read.

---

## Part 5 · What did we find? (in plain words)

1. **RetailCo sold more in 2024 but earned less.** Sales +6.7%, profit −6.6%.
2. **The Central region gives away too much in discounts.** On average it gives away 21.5% of list price, against about 13.5% in East and West. Its profit margin is only 3.3%.
3. **Tables and bookcases lose money in every region.** They are priced too thinly to survive the discounts they get.
4. **Any discount of 30% or more loses money.** Overall, those sales lost $249K.
5. **South is shrinking**, but it is still profitable. It needs more customers, not cheaper prices.
6. **West and East are healthy** and deliver all of the growth.

**What should management do?** Require approval for big discounts (trying it in Central first), fix table/bookcase pricing, reward salespeople for profit and not just sales, and investigate why South is losing customers.

---

## Part 6 · How to run it yourself

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/pipeline.py --regenerate    # rebuilds data, cleaning, charts
python tests/test_pipeline.py          # checks the cleaning is correct
jupyter notebook notebooks/            # open 01, then 02, 03, 04
```

## Part 7 · Suggested reading order

1. This file
2. [`docs/end_to_end_logic.md`](docs/end_to_end_logic.md): how every stage connects, following one real order line
3. [`docs/company_scenario.md`](docs/company_scenario.md): the business story
4. [`docs/data_dictionary.md`](docs/data_dictionary.md): the columns
5. Notebooks 01 → 04 (run each cell and read the explanation above it)
6. [`sql/sales_analysis.sql`](sql/sales_analysis.sql): SQL from basics to window functions
7. [`powerbi/POWER_BI_MASTER_GUIDE.md`](powerbi/POWER_BI_MASTER_GUIDE.md): build the dashboard, the one guide to follow (concepts: [`POWER_BI_STEP_BY_STEP.md`](powerbi/POWER_BI_STEP_BY_STEP.md))
8. [`reports/Business_Insights.md`](reports/Business_Insights.md) and [`Executive_Summary.md`](reports/Executive_Summary.md)
9. [`docs/project_story.md`](docs/project_story.md) → [`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md) → [`docs/PLACEMENT_READINESS.md`](docs/PLACEMENT_READINESS.md): practise explaining it
