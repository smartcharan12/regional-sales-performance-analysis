# Resume Bullets

**Rules used:** only verified facts from this repository; the synthetic data is mentioned; no "production", "real-time" or "client" claims. The Power BI work is described as **designed / specified** until you have actually built and validated the `.pbix`. Once you have, you may change "designed" to "built" (marked ⟨…⟩ below).

**Project title line:**
**Regional Sales Performance Analysis** | Python, pandas, SQL (MySQL), Power BI/DAX | GitHub: ⟨link⟩

---

## 1. Three concise bullets
- Built an end-to-end sales analytics pipeline in Python (pandas) on an 11.5K-row synthetic Superstore-style dataset, repairing 275 values and removing 106 invalid/duplicate rows, with every cleaning step logged and verified by 10 automated tests.
- Diagnosed why 2024 profit fell 6.6% while sales grew 6.7%: deep discounts (≥30%) lost $249K, and one region's 3.3% margin was associated with heavier discounting rather than product mix.
- Modelled the data as a star schema in MySQL 8 (totals reconciled with Python to the cent) and ⟨designed⟩ a 5-page Power BI dashboard with ~30 DAX measures, including YoY time intelligence.

## 2. Four stronger bullets
- Engineered a reproducible Python data pipeline (generate → clean → feature engineering → star-schema export → charts) for an 11,567-row synthetic Superstore-style dataset with injected data-quality defects. Repaired 275 values (e.g. rebuilt missing regions from state) instead of deleting rows, keeping 99.1% of records.
- Verified data quality with 10 automated tests against a known ground truth (repaired values, row counts, weighted margins, schema integrity), and reconciled every headline KPI across Python and MySQL to the cent.
- Performed EDA and root-cause analysis across regions, products, customers and discount levels. Showed that every discount level ≥ 30% was loss-making (−$249K), identified Tables/Bookcases as loss-making in all regions, and sized a discount-cap opportunity at ≤ $264K (labelled as an upper bound).
- ⟨Designed⟩ a Power BI star-schema model with ~30 DAX measures (SAMEPERIODLASTYEAR, RANKX, weighted effective discount) and a 5-page stakeholder dashboard, with documented expected values for every measure, and translated findings into owner-assigned recommendations.

## 3. Highly technical version
- Built a seeded Python/pandas ETL pipeline: synthetic Superstore-schema data generation with 11 injected defect classes; ordered, idempotent cleaning functions with an audit log and assertion-based validation; IQR outlier flagging; and star-schema export (1 fact + 4 dimension tables with referential-integrity checks). Covered by 10 ground-truth tests and verified on pandas 2.2 and 3.0.
- Implemented the schema in MySQL 8 with PK/FK/CHECK constraints and `LOAD DATA`. Wrote analytical SQL with CTEs and window functions (LAG, RANK, DENSE_RANK, NTILE, running SUM) for YoY growth, ranking, customer concentration and loss attribution. Results matched pandas to the cent.
- Specified a Power BI model (single-direction 1:* relationships, marked date table) with ~30 DAX measures including time intelligence, `ALLSELECTED`-based shares and a `SUMX` what-if measure.

## 4. Data Analyst / BI version
- Analysed 4 years of synthetic retail sales (11.5K order lines) to explain why profit fell 6.6% while sales rose 6.7%. Isolated deep discounting (≥ 30%, −$249K) and a low-margin region (3.3% vs 13.2%) as the main drivers.
- Cleaned and validated the data in Python (275 values repaired, 99.1% of rows kept, 10 automated checks) and reconciled every KPI in MySQL.
- ⟨Designed⟩ a 5-page Power BI dashboard (executive, regional, product, customer, profitability) with ~30 DAX measures and a validation checklist. Delivered recommendations with owners and KPIs, including a discount-approval pilot.

## 5. General SDE / analytics version
- Developed a modular, tested Python data pipeline (pandas, NumPy, Matplotlib) with a single-command reproducible run, 10 automated tests against ground truth, and cross-platform-safe outputs. Verified on two pandas major versions.
- Designed a relational star schema in MySQL 8 with integrity constraints, and wrote analytical SQL (CTEs, window functions) whose results matched the Python implementation exactly.
- Turned the analysis into a documented decision-support deliverable: KPI definitions, a BI dashboard specification with ~30 DAX measures, and evidence-based recommendations.

---

### Facts you can be asked to back up
| Claim | Evidence |
|---|---|
| 11,567 → 11,461 rows; 106 removed (70 duplicates) | `data/processed/cleaning_log.csv`, notebook 02 |
| 275 values repaired | `count_repaired_values()`, test `test_repaired_value_count` |
| 10 tests | `python tests/test_pipeline.py` |
| MySQL matches Python to the cent | `sql/sales_analysis.sql` A1 vs notebook 04 |
| Sales +6.69%, profit −6.63% (2024) | notebook 04, `sql/business_queries.sql` BQ2 |
| ≥ 30% discounts: −$249,356 | notebook 03/04, `Deep Discount Profit` |
| ~30 DAX measures | `powerbi/DAX_VALIDATION_CHECKLIST.md` (31) |
