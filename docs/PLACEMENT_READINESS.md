# Placement Readiness

Use this page the week before interviews. Full Q&A bank: [INTERVIEW_GUIDE.md](../INTERVIEW_GUIDE.md) (90 questions). Story version: [project_story.md](project_story.md).

---

## Skills demonstrated (and where)

| Skill | Where in the project | What you can show |
|---|---|---|
| Python | `src/*.py` | Modular pipeline, functions with docstrings, one-command run |
| pandas | `src/data_cleaning.py`, `src/eda.py` | `groupby/agg`, `pivot_table`, `merge`, type conversion, `drop_duplicates` |
| NumPy | generator, tests | Seeded random generation, `np.isclose` for safe float comparison |
| Matplotlib | `src/eda.py` | 13 purpose-driven charts with consistent styling |
| Seaborn | `src/eda.py` heatmap | Diverging-colour profitability matrix |
| SQL | `sql/*.sql` | SELECT → JOIN → CASE → CTE → window functions |
| MySQL | `sql/schema.sql` | PK/FK/CHECK constraints, `LOAD DATA`, views; run on MySQL 8.0 |
| Data cleaning | notebook 02 | Fix-before-delete decisions, audit log, ground-truth tests |
| EDA | notebook 03 | Regional, time, product, customer and discount analysis |
| Statistics | notebook 03 | Median vs mean, IQR outliers, Pearson/Spearman, CAGR, weighted ratios |
| Feature engineering | `src/feature_engineering.py` | Gross sales, discount amount, margin, date parts |
| Power BI | `powerbi/Dashboard_Design.md` | 5-page design *(build in Power BI Desktop)* |
| Power Query | `powerbi/Data_Model.md` | M code with parameters and typed columns |
| DAX | `powerbi/DAX_Measures.md` | 31 measures: CALCULATE, time intelligence, RANKX, SUMX *(Power BI Desktop validation required)* |
| Data modeling | `powerbi/Data_Model.md` | Star schema, 1:* relationships, filter direction |
| Business analysis | notebook 04 | 17 business questions, KPI definitions, hypothesis testing |
| Data storytelling | `reports/` | Fact → explanation → investigation → action |
| Git/GitHub | `docs/GITHUB_PUBLISHING.md` | Clean repo, `.gitignore`, `.gitattributes` |

## The 20 most likely interview questions

1. Tell me about your project.
2. Why did you choose this project?
3. Where did the data come from? Is it real?
4. How did you clean the data?
5. How did you handle missing values?
6. Why did you remove duplicates, and how did you tell real duplicates from repeated Order IDs?
7. What is the difference between sales, profit and profit margin?
8. What was your most important finding?
9. What tools did you use, and why each one?
10. What is a star schema? Fact vs dimension table?
11. What is the difference between WHERE and HAVING?
12. What is a window function? Give an example from your project.
13. What is DAX? Measure vs calculated column?
14. How did you calculate year-over-year growth?
15. Which chart did you use for X, and why?
16. How did you validate your numbers?
17. What recommendation did you make?
18. What are the limitations of your analysis?
19. What would you do differently, or with real data?
20. How would a manager use your dashboard?

## 15 questions that expose weak understanding

1. Why is averaging the row-level profit margins wrong? What number does it give here? *(11.7% vs 10.3%)*
2. Your Order ID repeats. Why didn't you remove those as duplicates?
3. Why didn't you delete the outliers?
4. `COUNT(*)` vs `COUNT(DISTINCT order_id)`: which gives "orders", and why?
5. What exactly is filter context? What happens to `[Total Sales]` inside a Central bar?
6. What does `CALCULATE` do to the filters?
7. Why does `SAMEPERIODLASTYEAR` need a marked, continuous date table?
8. What happens to your YoY measure when no year is selected, and how did you handle it?
9. `ALL` vs `ALLSELECTED`: when would `Sales Share %` give a wrong answer?
10. Your data is synthetic. Didn't you just find what you put in?
11. Correlation of −0.81: does that prove discounts cause losses?
12. How did you rule out product mix as the reason for Central's low margin?
13. The $264K: why is it an upper bound and not a forecast?
14. Why single-direction relationships rather than bi-directional?
15. If MySQL and Python disagreed by $50, how would you find the cause?

*(Answers: INTERVIEW_GUIDE Q79, Q11, Q24, Q39, Q48, Q46, Q54, DAX_Measures Part 4, Q49, Q68, Q69, Q87/Business_Insights #2, Q59, Q53. For #15: compare row counts first, then totals by year, then by region, until the difference is isolated to specific rows.)*

## What you absolutely must understand (learning checklist)

**Data & cleaning**
- [ ] The grain: one row = one product on one order
- [ ] Why each cleaning decision was *repair*, *remove* or *flag*, and the numbers (106 removed, 275 repaired)
- [ ] How the tests prove the cleaning, and why that's only possible with synthetic data

**Analysis**
- [ ] Sales vs Gross Sales vs Profit vs Margin vs Effective Discount
- [ ] Weighted margin, and why the average of row margins is wrong
- [ ] Median vs mean on skewed data; the IQR rule; Pearson vs Spearman; CAGR
- [ ] The Central test (discount vs product mix), and why it's still an association

**SQL**
- [ ] Every query type in `sales_analysis.sql`, explained without looking
- [ ] `LAG` for YoY, `RANK`/`DENSE_RANK`, `NTILE`, `SUM() OVER ()`
- [ ] PK, FK and CHECK constraints in `schema.sql`

**Power BI / DAX**
- [ ] Star schema: fact vs dimension, PK/FK, one-to-many, single direction
- [ ] Measure vs calculated column; filter context; `CALCULATE`
- [ ] `SAMEPERIODLASTYEAR`, `HASONEVALUE`, `ALLSELECTED` vs `REMOVEFILTERS`
- [ ] Be able to build at least `Total Sales`, `Profit Margin %` and `YoY Sales Growth %` live, from memory

**Business**
- [ ] The 5 headline facts and the 3 main recommendations
- [ ] The limitations, stated before the interviewer finds them

## 90-second project explanation

> "This project tackles a classic problem: a retailer whose sales went up in 2024 but whose profit went down, and nobody could say why.
>
> I couldn't use real company data, so I wrote a Python generator that creates about 11,500 order lines in the Superstore format, with realistic mess built in: duplicates, missing regions, prices stored as text. Because I kept the clean version, I could actually test my cleaning instead of just trusting it.
>
> I cleaned it with a fix-before-delete approach. For example, a blank region can be rebuilt from the state. I repaired 275 values, removed 106 rows (70 of them duplicates), and ten tests confirm the result matches the truth.
>
> The analysis showed sales up 6.7% but profit down 6.6%. Digging in, one region, Central, kept only about 3 cents per dollar against 13 in the East. Tables and Bookcases lost money everywhere. And every discount of 30% or more lost money overall, about $249K. I tested whether Central's problem was its product mix or its discounting, and the evidence pointed to discounting, though *why* it discounts more is a question for the business.
>
> I put the data into MySQL as a star schema to double-check every number, and they matched Python to the cent. Then I designed a five-page Power BI dashboard with about 30 DAX measures, with expected values written down so it can be validated.
>
> My main recommendation was an approval rule for discounts of 30% or more, piloted in Central first and measuring both margin and volume. I sized the upside at up to $264K, explicitly as an upper bound."

*(If you have built the `.pbix` by then, change "designed … so it can be validated" to "built and validated".)*
