# Interview Guide: Regional Sales Performance Analysis

How to explain this project confidently, and answer the follow-up questions.

> **Golden rule: be honest about the data.** Say upfront that it is synthetic, generated with documented rules. Interviewers respect this. It also opens your strongest talking point: *you could test your cleaning against a known truth.* Never present the findings as facts about a real company.

## What you can and cannot claim

| ✅ You can say | ❌ Don't say (unless it becomes true) |
|---|---|
| "I designed the Power BI data model, ~30 DAX measures and a 5-page dashboard, with expected values for validation" | "I built and validated the dashboard". Only say this **after** you've built the `.pbix` and ticked `DAX_VALIDATION_CHECKLIST.md` |
| "The SQL runs on MySQL 8 and matches Python to the cent" | "It runs in production" / "real-time" |
| "The dashboard images in the repo are design mockups I rendered in Python from the data" | "These are screenshots of my Power BI dashboard" (they aren't) |
| "The data is a synthetic, Superstore-style dataset I generated with documented rules" | "Company data", "client data", "I worked with RetailCo" |
| "The findings show how I'd diagnose a profit problem" | "Discounts cost the company $264K" (it's a synthetic upper bound) |

## Numbers to memorise

| | |
|---|---|
| Rows | 11,567 raw → **11,461 clean** (99.1% kept); 70 duplicates, 36 untrusted rows removed; 275 values repaired |
| Size | **$4.39M** sales, **$452K** profit, **10.3%** margin, 5,190 orders, 741 customers, 2021–2024 |
| Headline | 2024: sales **+6.7%**, profit **−6.6%** |
| Central | **3.3%** margin; **21.5%** effective discount vs ~13.5% East/West |
| Products | Tables **−$91.5K**, Bookcases **−$30.4K**; Furniture break-even |
| Discounts | ≥30% always loss-making: **−$249K**; r = −0.81 |
| What-if | up to **$264K** (upper bound, same volume assumed) |

---

## Part 1 · Explaining the project

### 30-second version
> "I built an end-to-end sales analytics project for a fictional retailer whose sales grew in 2024 while profit fell. I cleaned about 11,500 order lines in Python, with every decision logged and tested, analysed them, modelled them as a star schema in MySQL and Power BI, and designed a five-page dashboard with DAX measures. The main finding was that deep discounting, concentrated in one region and one product group, wiped out the growth. Every discount of 30% or more lost money. I recommended a discount-approval pilot in that region."

### 1-minute version
> "The business question was: sales are up but profit is down — why? I used a synthetic dataset with the Superstore layout, generated from documented rules with realistic errors injected, so I could share it and test my cleaning against the true values.
>
> In Python I profiled and cleaned the data. I repaired 275 values, for example rebuilding missing regions from the state, and removed only 106 rows, 70 of which were exact duplicates. A test suite confirms every repaired value matches the truth.
>
> EDA showed 2024 sales up 6.7% but profit down 6.6%. The Central region had a 3.3% margin against 13% in the East, because it discounts much more heavily on the same products. Tables and bookcases lost money in every region.
>
> I loaded a star schema into MySQL to cross-check the numbers, and designed a Power BI model with about 30 DAX measures, including year-over-year time intelligence. My recommendations were a discount-approval pilot in Central, a pricing review for tables, and putting margin into sales targets."

### 3-minute version (structure: Problem → Data → Method → Findings → Impact)
1. **Problem (20 s):** RetailCo's leadership saw sales grow but profit fall, and the existing reports showed revenue only. They wanted a regional view of profitability and a dashboard.
2. **Data (30 s):** 11,567 order lines, 2021–2024, Superstore column layout. It is synthetic: I wrote a generator with explicit business rules and injected realistic errors, including duplicates, `$1,234` stored as text, inconsistent region spellings, impossible dates and discounts typed as 20 instead of 0.2. I chose this so I could share the data and **prove** my cleaning was correct.
3. **Cleaning (40 s):** principle: fix before delete. Region was rebuilt from State after I verified each state maps to one region. Names came from IDs. Percent-style discounts were rescaled only when the result was a valid policy level. Rows were removed only when money was missing or values were impossible. Outliers were flagged, not removed, because they were genuine copiers and tables worth 42% of revenue. Everything is logged, and ten tests check the output against ground truth.
4. **Analysis (40 s):** I always used weighted margin, SUM(profit)/SUM(sales). The findings: 2024 margin fell from 10.6% to 9.2%. Central had a 3.3% margin and the highest effective discount in 15 of 17 sub-categories. On its normally discounted lines, Central's margin was 17.4%, about the same as the other regions, which pointed to discounting rather than product mix. Tables lost money even at ordinary 10–20% discounts, so that is a pricing problem as well.
5. **BI (30 s):** star schema in MySQL with PK/FK constraints, and the totals match Python to the cent. In Power BI I designed the model, about 30 DAX measures (`SAMEPERIODLASTYEAR`, `RANKX`, effective discount, a what-if measure) and five dashboard pages, one per stakeholder.
6. **Impact (20 s):** recommendations with owners and KPIs: discount approval ≥30% piloted in Central, Tables pricing review, margin-based incentives. I sized the opportunity at up to $264K, clearly labelled as an upper bound because volume would drop.

### 5-minute deep version
Use the 3-minute structure and add:
* **Why the grain matters:** Order ID repeats are multi-product orders, not duplicates. Counting rows ≠ counting orders, so I use `DISTINCTCOUNT(Order ID)`.
* **A mistake I avoided:** averaging row-level margins gives 11.7%; the correct weighted margin is 10.3%. Notebook 02 demonstrates this.
* **The test I ran on Central:** two hypotheses, product mix vs discounting. I compared effective discount within each sub-category and margin on lines under 30% discount. This is evidence for discounting, but I present it as an association; the *reason* needs interviews.
* **A real bug the tests caught:** my first generator turned some 0% discounts into "20", which cleaning then correctly read as 20%. The test against ground truth caught the mismatch. I fixed the generator, because a real system would never record a 0% discount as 20.
* **SQL validation:** I ran all scripts on an actual MySQL 8.0 server; for example, a column named `year_month` had to be renamed because it is a reserved word.
* **What I'd do next:** an A/B test for the discount cap; add shipping and returns costs; add a targets table for plan-vs-actual.

---

## Part 2 · Interview questions & answers

### Must-answer questions: where to find each answer

| Question | Answer |
|---|---|
| Explain your project | [PLACEMENT_READINESS.md › 90-second explanation](docs/PLACEMENT_READINESS.md#90-second-project-explanation), Part 1 above |
| Why did you choose this project? | Q74 |
| Where did the data come from? / Why synthetic? | Q3, Q75 |
| Why didn't you use a real company dataset? | Q76 |
| How did you clean the data? | Q18, Q77 |
| Why did you remove some rows? | Q19, Q20, Q72 |
| Why repair some values instead of deleting them? | Q78 |
| Sales vs profit? What is profit margin? | Q55, Q56 |
| Why weighted profit margin? | Q79 |
| Why SQL? Why Python? | Q80, Q81 |
| Why Power BI? Why not Python charts? | Q65, Q82 |
| Star schema, fact table, dimension table | Q51, Q83 |
| Primary key, foreign key, one-to-many | Q84, Q52 |
| What is DAX? Measure vs calculated column? Filter context? | Q85, Q45, Q48 |
| How did you validate your numbers? How do you know the analysis is correct? | Q86, Q87 |
| Most important finding? Recommendation? | Q4, Q88 |
| Limitations? Improving it with real company data? | Q89, Q90 |

### 1. Project overview
**Q1. What problem does the project solve?**
Leadership saw sales growing but profit falling and couldn't explain it. The project finds where profit is lost (by region, product, discount) and gives a dashboard and recommendations.

**Q2. Who are the users?**
CEO (overall health), sales manager (regions and customers), regional managers (their own region), finance (profit leakage), category manager (products). Each dashboard page targets one of them.

**Q3. Is the data real?**
No, it is synthetic. I generated it with documented rules in the Superstore layout and injected known errors. Benefits: it can be shared, it needed real cleaning, and I could test the cleaning against ground truth. The pipeline runs unchanged on the real Superstore file.

**Q4. What was the most important finding?**
2024 sales grew 6.7% while profit fell 6.6%. The cause traces to deep discounts, especially in Central and on Tables. Every discount level of 30% or more loses money in total.

**Q5. What was the hardest part?**
Deciding *what not to delete*. For example, outliers looked suspicious statistically but were genuine high-value products worth 42% of revenue. And ship dates before order dates: the sale was real, only the ship date was wrong.

### 2. Python
**Q6. Why put logic in `.py` modules instead of only notebooks?**
Notebooks are for explanation; modules are for reusable, testable logic. The notebooks import the modules, so the explanation and the pipeline can't disagree, and the tests can import the same functions.

**Q7. How is the project reproducible?**
Fixed random seed, all paths relative to the project root, and one command, `python src/pipeline.py --regenerate`, rebuilds everything. A test confirms the committed raw file equals the generator's output.

**Q8. How did you test a data pipeline?**
Ten tests: the raw file is byte-identical to the seeded generator output, no invented rows, repaired values equal ground truth, removed rows match the log, totals within 1% of truth, group margins are weighted, the repaired-value count, the headline numbers quoted in the docs, LF line endings, and star-schema integrity (no lost rows, continuous date table).

**Q9. What does `assert` do in your cleaning code?**
It stops the program if a rule is broken (e.g. a Region outside the four valid values). A failed check is better than a silently wrong dashboard.

### 3. Pandas
**Q10. Difference between `df.info()` and `df.describe()`?**
`info()` shows column types and non-null counts (structure). `describe()` shows statistics such as mean, min and quartiles (content). I used `info()` to find Sales stored as text, and `describe()` to find negative quantities and discounts above 1.

**Q11. How did you find duplicates?**
`df.duplicated()` for rows identical in every column. Separately, I checked `Order ID + Product ID`, the true key. Order ID alone repeats legitimately.

**Q12. `groupby` + `agg`: what does it do?**
It splits rows into groups (e.g. by Region), calculates something per group (sum of Sales, distinct count of Order ID), and combines the results into one table.

**Q13. Why `nunique` for orders?**
Each order has several rows, so `count` would count lines. `nunique("Order ID")` counts orders.

**Q14. How did you convert `"$1,277.10"` to a number?**
`str.replace(r"[$,]", "", regex=True)` and then `pd.to_numeric(..., errors="coerce")`. The `coerce` option turns anything still invalid into NaN, so I can count and inspect it instead of the code crashing.

**Q15. `pivot_table` vs `groupby`?**
Both aggregate; `pivot_table` reshapes one grouping into columns (e.g. regions as rows, years as columns), which is ideal for YoY comparison.

### 4. NumPy
**Q16. Where did you use NumPy?**
Random generation with a seeded `default_rng`, log-scaling for the sales histogram, `np.allclose` in the tests to compare floating-point numbers safely, and vectorised calculations under pandas.

**Q17. Why `np.allclose` instead of `==` for money?**
Floating-point numbers can differ in tiny decimal places after arithmetic; `allclose` compares within a tolerance.

### 5. Data cleaning
**Q18. How did you handle missing values?**
It depends on the column. Region was rebuilt from State (verified one-to-one). Names were looked up from IDs. Missing Sales/Profit rows were removed, because there was no price or cost column to rebuild them, and imputing would invent money. That was 17 rows, 0.15%.

**Q19. Why not fill missing Sales with the mean?**
The mean sale is $383, but the median is $139, and a pen line might be $5. Imputing would fabricate revenue and distort every KPI. With 17 rows, deleting changes nothing material.

**Q20. Why did you remove duplicates?**
The 70 rows were identical in every column, which means the same line was exported twice, so it would double-count revenue. I didn't touch repeated Order IDs.

**Q21. How do you know cleaning didn't remove useful information?**
Of 106 removed rows, 70 were exact copies, so nothing was lost there. The other 36 (0.3%) had missing or impossible values. I repaired 275 values instead of deleting them. Tests show totals are within 1% of the true data and every repaired value is correct. The cleaning log documents each step.

**Q22. Why fix discounts `20 → 0.2`, but not other invalid values?**
Because the intent is unambiguous: 20/100 = 0.20 is an allowed policy level. I only rescale when the result is valid; anything else would be removed (there were none).

**Q23. Why standardise text before removing duplicates?**
`" West"` and `"West"` would otherwise make two identical sales look different, hiding a duplicate.

**Q24. How did you treat outliers?**
I detected them with the IQR rule (above Q3 + 1.5×IQR ≈ $1,170) and flagged them, but kept them. They are genuine copiers, phones and tables worth 42% of revenue; removing them would understate Technology and Furniture.

**Q25. A ship date was before the order date. Why keep the row?**
The sale itself was valid; only shipping info was wrong. I set Ship Date to missing, so it is excluded from the shipping analysis only, and kept the revenue.

### 6. EDA
**Q26. What is EDA and why do it?**
Exploring data with summaries and charts to find patterns and anomalies before drawing conclusions. It generates the hypotheses that the business analysis then tests.

**Q27. Why a rolling average on the monthly chart?**
Monthly sales swing heavily with seasons. A 12-month rolling average removes the seasonal effect and shows the underlying trend.

**Q28. Why no pie charts?**
Comparing close values by angle is hard. Bars are compared by length, which people read accurately.

**Q29. Why not a dual-axis chart for sales and profit?**
The alignment of two y-axes is arbitrary and can suggest a relationship that isn't there. I used side-by-side panels with the same category order.

### 7. Statistics
**Q30. Mean vs median: which did you use?**
Sales are right-skewed (mean $383, median $139), so the median describes a typical line better. For business totals I use sums.

**Q31. What does a correlation of −0.81 mean?**
A strong negative association between discount and line margin: higher discount goes with lower margin. It doesn't prove causation by itself, although here the arithmetic mechanism (price falls, cost doesn't) makes causation plausible.

**Q32. Pearson vs Spearman?**
Pearson measures a straight-line relationship; Spearman measures any consistently increasing or decreasing one, using ranks, so it is less sensitive to outliers. I reported both: −0.81 and −0.72.

**Q33. What is CAGR and why use it?**
Compound annual growth rate = (last/first)^(1/years) − 1. It summarises a multi-year trend as one rate, which is fairer than comparing two adjacent years.

**Q34. What is the IQR rule?**
IQR = Q3 − Q1. Values above Q3 + 1.5×IQR or below Q1 − 1.5×IQR are statistical outliers. It is robust because quartiles aren't affected by extreme values.

### 8. SQL
**Q35. WHERE vs HAVING?**
WHERE filters rows *before* grouping; HAVING filters groups *after* aggregation, e.g. `HAVING SUM(profit) < 0` for loss-making products.

**Q36. What is a CTE?**
A named temporary result defined with `WITH name AS (...)`. It breaks a complex query into readable steps, e.g. first yearly totals, then YoY growth.

**Q37. What is a window function?**
A calculation across related rows that keeps every row instead of collapsing them, e.g. `LAG(sales) OVER (ORDER BY year)` for the previous year, or `RANK() OVER (ORDER BY margin DESC)`.

**Q38. How did you calculate YoY growth in SQL?**
Two ways: a self-join of a yearly CTE on `year = year − 1`, and `LAG()`. LAG is shorter. With `PARTITION BY region` it compares each region with its own previous year.

**Q39. Why `COUNT(DISTINCT order_id)`?**
Because the table is at order-line grain; `COUNT(*)` would count lines.

**Q40. Why use a date range instead of `YEAR(order_date) = 2024`?**
A function on the column prevents MySQL from using the index on `order_date`; a range (`>= '2024-01-01' AND < '2025-01-01'`) can use it.

**Q41. What constraints did you add, and why?**
Primary keys, foreign keys from the fact to each dimension, and CHECKs (sales > 0, quantity > 0, discount between 0 and 1), so bad data is rejected by the database itself.

### 9. Power BI
**Q42. What is Power Query used for here?**
Loading the CSVs, setting data types and a folder parameter. Heavy cleaning was already done in Python. I also documented how to build the star schema in Power Query as an alternative.

**Q43. Why sort Month by Month Number?**
Otherwise months sort alphabetically (Apr, Aug, Dec…).

**Q44. How would you show only one region to each regional manager?**
Row-level security: a role filtering `DimGeography[Region]` using `USERPRINCIPALNAME()` mapped through a user-region table.

### 10. DAX
**Q45. Calculated column vs measure?**
A column is computed per row at refresh, stored, and doesn't react to slicers. A measure is computed at query time for the current filter context. Margin must be a measure, otherwise you'd be summing or averaging row margins, which is wrong.

**Q46. What does CALCULATE do?**
It evaluates an expression under modified filters. For example, `CALCULATE([Total Sales], SAMEPERIODLASTYEAR(DimDate[Date]))` evaluates sales on the same dates shifted back a year.

**Q47. Why DIVIDE instead of `/`?**
It returns BLANK instead of an error when the denominator is zero, e.g. an empty selection.

**Q48. What is filter context?**
The set of filters active when a measure is evaluated: slicers, the row/column of a visual, and page filters. The same measure returns different numbers in different contexts.

**Q49. ALL vs ALLSELECTED vs REMOVEFILTERS?**
`ALL`/`REMOVEFILTERS` remove filters completely (company-wide totals). `ALLSELECTED` removes filters from the visual but keeps the user's slicer selections, which is right for a "share of the selected total".

**Q50. Why ABS in YoY Profit Growth?**
If last year's profit was negative, dividing by it flips the sign and an improvement would look like a decline.

### 11. Data modelling
**Q51. Why a star schema?**
Descriptions are stored once, filters flow predictably from dimension to fact, time intelligence needs a proper date table, and new facts (targets, returns) can share dimensions. At 11k rows a flat table would work too. I chose the star schema because it is the standard and it scales.

**Q52. What is cardinality?**
How many rows match across a relationship. Mine are all one-to-many: one product → many sales lines.

**Q53. Why single-direction filters?**
Bi-directional filters can create ambiguous filter paths and slow the model. All my questions flow from dimension to fact.

**Q54. Why does the date table need to be continuous?**
Time-intelligence functions shift dates; a gap would break `SAMEPERIODLASTYEAR`/`TOTALYTD`. My test asserts there are no gaps.

### 12. Business understanding
**Q55. Sales vs revenue vs profit vs margin?**
Sales = revenue after discount (the same thing here). Profit = sales minus cost of goods. Margin = profit ÷ sales, i.e. efficiency rather than size. Gross sales = value at list price.

**Q56. Why did you use Profit Margin instead of Profit?**
Profit favours big regions just because they are big. Margin shows how much of each dollar is kept, so different-sized regions can be compared fairly. I show both, because a high margin on tiny sales may not matter.

**Q57. What is effective discount, and why not average the Discount column?**
Discount given ÷ list-price value. A simple average treats a 50% discount on a $3 pen the same as one on a $3,000 copier; effective discount weights by money.

### 13. Scenario questions
**Q58. What happens if sales increase but profit decreases? How would you detect it?**
That is exactly 2024 here. Detect it by always pairing sales growth with profit growth or margin, and with a *Growth Gap* KPI (profit growth − sales growth; −13.3 pp in 2024). Then decompose the profit change by region, product and discount band to find where it came from.

**Q59. A manager wants to cut all discounts tomorrow. What do you say?**
The data supports controlling discounts of 30% and above, but we don't know how customers will react. I'd recommend a pilot in Central, measuring margin *and* volume against similar regions. The $264K figure is an upper bound assuming no volume loss.

**Q60. Next quarter's data arrives. What do you do?**
Drop the new export into `data/raw/`, run the pipeline and the tests, check the cleaning log for new kinds of errors, and refresh Power BI. In production, this would be a scheduled job plus a scheduled dataset refresh.

### 14. Dashboard questions
**Q61. How would you validate your dashboard?**
I prepared the expected value of every measure before building it, from Python and confirmed in SQL (`powerbi/DAX_VALIDATION_CHECKLIST.md`). Validation means reconciling the cards against those values: Total Sales $4,391,176.00, Orders 5,190, then filtered values such as Central margin 3.28% and 2024 sales YoY +6.69%. I'd also check that the row count of each table matches, and have a user answer the business questions from the dashboard. *(Once you've built it, say "I validated it against…". Until then, say "my validation plan is…".)*

**Q62. How would you optimise a slow Power BI dashboard?**
Use Performance Analyzer to find the slow visual; keep the star schema with single-direction relationships; remove unused columns; prefer measures over calculated columns; avoid `FILTER` over whole tables; reduce visuals per page; for big data use aggregations, incremental refresh or DirectQuery for detail only.

**Q63. Why did you choose this visualization?** *(give a concrete example)*
For "which region keeps the most profit per dollar", I used a horizontal bar chart: regions are categories and margin is one number, and bars are compared by length. I added a reference line at the company margin so above/below average is instant, and I use red only for regions below it.

**Q64. How would you deploy this dashboard in a real company?**
Publish to a Power BI Service workspace, connect to the company database through a gateway, schedule a daily refresh, apply row-level security per region, distribute as an App, and set alerts on the margin KPI. Version-control the report (PBIP format) with the repository.

### 15. Difficult cross-questioning
**Q65. Why did you use Power BI when you already used Python?**
They serve different audiences. Python is where I clean, test and explore: work for analysts. Managers need to click a region or year and get an answer instantly, without running code. Power BI gives them that, refreshes automatically, and controls who sees what.

**Q66. Why not do everything in Power BI?**
Power Query can clean data, but complex rules (lookups, conditional fixes, validation) are harder to read, version and unit-test there. I keep transformation logic upstream in tested Python and use Power BI for modelling and interaction. In a smaller self-service setting, doing more in Power Query is a reasonable trade-off.

**Q67. Why use DAX instead of Python for the KPIs?**
Python computes the combinations I think of in advance. DAX computes the KPI for *any* combination a user selects, at click time. For a static report Python is enough; for an interactive one you need measures.

**Q68. Your data is synthetic, so didn't you just find the patterns you put in?**
Yes, the patterns come from rules I wrote, and I say so. The project demonstrates the *method*: diagnosing a profit problem from noisy, messy data. The findings had to be recovered through cleaning, noise and aggregation, and the tests prove the cleaning recovered the truth. The same code runs on real data unchanged.

**Q69. Isn't "discounts cause losses" just correlation?**
For the mechanism, no: a discount lowers price while cost stays the same, so it is arithmetic. What *is* uncertain is the counterfactual: would those sales have happened at a lower discount? That is why I recommend a pilot, and why the $264K is labelled an upper bound.

**Q70. What if management disagrees with your findings?**
First, listen; they may know something the data doesn't, such as a strategic customer or a competitor event. Then walk through the evidence together using the dashboard, separating facts from my interpretations. Agree on a test (the Central pilot) that would settle it. My job is to make the evidence clear, not to win the argument.

**Q71. Central sells the same products. Couldn't higher costs explain its low margin?**
Possibly. Costs beyond cost of goods aren't in the data. But Central's margin on normally discounted lines (17.4%) matches the other regions (18.0%), which suggests the cost of goods is similar. Freight or overheads would need separate data.

**Q72. You removed 36 real rows. Couldn't that bias the result?**
That is 0.3% of rows, spread across regions and years, and the tests show totals within 1% of the truth. I logged them so anyone can check. Rebuilding them would have meant inventing money.

**Q73. What would you do differently?**
Add returns and shipping costs, add a targets table for plan-vs-actual, and with real data, interview the regional managers before finalising recommendations.

### 16. Fundamentals you must answer fluently
**Q74. Why did you choose this project?**
Because "sales are up but profit is down" is one of the most common questions a business analyst actually gets, and answering it touches the whole job: messy data, cleaning decisions, KPIs, SQL, a BI model, and recommendations a manager can act on. I wanted one project that shows the full workflow rather than a single notebook.

**Q75. Where did the data come from?**
I generated it with a Python script I wrote, `src/generate_data.py`. It uses the same columns as the well-known Superstore sample, with explicit rules for regional growth, discount habits, product margins and seasonality. It also adds a known set of realistic errors: duplicates, typos, missing values, text in number columns and impossible dates. The random seed is fixed, so anyone gets exactly the same file.

**Q76. Why not use a real company dataset?**
Three reasons. Real company data is confidential, so I couldn't publish it. Public samples like Superstore are already clean and used in thousands of portfolios, so there's nothing real to clean. And with real data there's no way to *check* that the cleaning is correct. With my own data I keep the error-free version, so my tests can prove every repaired value is right. The trade-off is that the findings reflect the rules I wrote, which is why I present them as a demonstration of the method.

**Q77. Walk me through your cleaning.**
In order: trim spaces; standardise Region (rebuilt from State) and Category (rebuilt from Sub-Category); convert `"$1,277.10"` text to numbers; remove 70 exact duplicate rows; rescale discounts typed as 20 to 0.20; fill missing names from their IDs; remove 5 rows with impossible order dates and blank 6 impossible ship dates; remove 17 rows missing Sales or Profit and 14 with zero or negative sales/quantity; then flag outliers without deleting them. Every step is logged with a before/after row count.

**Q78. Why repair some values instead of deleting the rows?**
Because the rest of the row is real. A sale in Houston with a blank Region is still a real sale. Deleting it would understate Central's sales, and the correct value can be looked up: Texas is always Central. I only delete when the missing value can't be rebuilt *and* matters, like a sale with no amount.

**Q79. Why use a weighted profit margin?**
Margin for a group is total profit ÷ total sales, so every dollar counts once. If you average the margin of each line instead, a $3 pen counts as much as a $3,000 copier. In this data that wrong method gives 11.7% instead of the true 10.3%. In DAX it's the difference between a measure and an averaged calculated column.

**Q80. Why did you use SQL?**
Because in real companies the data lives in databases, and SQL is how analysts get it out. I also used it as an independent check: the same totals computed by MySQL matched Python to the cent. And the database enforces rules itself (primary keys, foreign keys, `CHECK (sales > 0)`), so bad data can't sneak in later.

**Q81. Why did you use Python?**
For the work that needs logic and testing: cleaning rules, validation and exploratory analysis. Python lets me write each cleaning step as a function, log what it changed, and test it automatically. That's much harder to do in Excel or Power Query.

**Q82. Why Power BI instead of Python charts?**
Python charts are static pictures of questions I chose. A manager wants to pick their own region, year or product and get the answer immediately, without code. Power BI does that, refreshes on a schedule, and can restrict each manager to their own region. I use Python charts for analysis and Power BI for communication.

**Q83. What are a star schema, a fact table and a dimension table?**
A **fact table** stores events with numbers: in my case one row per order line, with Sales, Profit and Quantity. A **dimension table** stores descriptions you filter by: customers, products, places and dates, each listed once. A **star schema** is the fact table in the middle with the dimensions around it, linked by keys. It's the standard design for BI because filters flow cleanly from a dimension into the facts.

**Q84. What are a primary key and a foreign key? Why one-to-many?**
A **primary key** uniquely identifies a row in its table: `Product ID` in `DimProduct`. A **foreign key** is the same column in another table that points back to it: `Product ID` in `FactSales`. The relationship is **one-to-many** because one product appears once in the product table but on many sales lines. The "one" side must be unique, otherwise Power BI couldn't tell which description belongs to a sale.

**Q85. What is DAX?**
DAX is Power BI's formula language. Its key feature is that a measure is written once but calculated for whatever is selected. `Total Sales = SUM(FactSales[Sales])` shows the company total on a card, Central's total in a Central bar, and 2024's total when the slicer says 2024.

**Q86. How did you validate your numbers?**
Three independent ways. First, the tests compare my cleaned data with the error-free original. Second, I recomputed the key results in MySQL, and they matched Python to the cent. Third, a test pins the headline numbers quoted in the documentation, so the docs can't silently drift from the data. For Power BI, I prepared an expected value for every measure, to check against once it's built.

**Q87. How do you know your analysis is correct?**
For the numbers: the validation above. For the conclusions: I only state as fact what the data directly shows, I keep explanations labelled as hypotheses, and I tested the competing explanation for Central (product mix vs discounting) instead of assuming. What I *can't* know from transactions alone is *why* Central discounts more. That needs conversations with the business, and I say so.

**Q88. What business recommendation did you make?**
The main one: require manager approval for discounts of 30% or more, piloted in the Central region first, and measure both margin and order volume against other regions. Also: re-price or renegotiate Tables and Bookcases, add margin to sales targets, and investigate why South is losing volume before spending on promotions.

**Q89. What are the limitations?**
The data is synthetic, so findings illustrate the method. Only cost of goods is included, not shipping, returns or overheads. Associations aren't proof of cause; the reasons behind discounting need business input. The $264K what-if assumes customers would buy the same amount at a higher price, so it is an upper bound. There are no targets or budgets. And the Power BI report still has to be built and validated in Power BI Desktop.

**Q90. How would you improve this with real company data?**
Point the same pipeline at the company's database (the column layout is standard), then: re-run the data-quality checks, since real data will have new kinds of errors; add returns, shipping costs and targets; interview regional managers to explain the discount patterns; run the Central discount pilot as a proper controlled test; and publish the dashboard to the Power BI Service with scheduled refresh and row-level security.

---

## Part 3 · "Tell me about your Regional Sales Performance Analysis project."

The 90-second answer lives in one place, so it never goes out of date: **[docs/PLACEMENT_READINESS.md › 90-second project explanation](docs/PLACEMENT_READINESS.md#90-second-project-explanation)**. For a story-style version to practise from, see [docs/project_story.md](docs/project_story.md).

**Likely follow-ups:** "How did you clean it?" (Q77) · "Why star schema?" (Q51, Q83) · "How do you know discounts cause it?" (Q69) · "Why synthetic?" (Q75, Q76) · "How did you validate?" (Q86).
