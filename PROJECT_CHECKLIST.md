# Project Checklist

`[x]` = done **and actually executed/checked** · `[ ]` = still to do. Nothing is ticked on the basis of "should work".

Last full verification run: Linux, Python 3.12, from a clean state (all generated outputs deleted first).

---

## ✅ Automatically verified

### Reproducibility (executed)
- [x] `python src/pipeline.py --regenerate` rebuilds everything from nothing: raw data (11,567 rows) → clean data (11,461 rows, 275 values repaired) → 5 star-schema CSVs → 13 charts
- [x] `python tests/test_pipeline.py`: **10/10 tests pass**
  - raw file byte-identical to the seeded generator · no rows invented · repaired values equal ground truth · removed rows match the log · totals within 1% of truth · group margins are weighted · 275 repaired values · headline numbers quoted in the docs · LF line endings · star-schema integrity
- [x] All 4 notebooks executed top to bottom (`jupyter nbconvert --execute`): **0 errors, 0 unexecuted cells** (21 + 20 + 32 + 10 code cells)
- [x] Notebook 02 writes a `sales_cleaned.csv` byte-identical to the pipeline's
- [x] Compatibility: on **pandas 2.2.3 / NumPy 1.26.4**, the pipeline and all 10 tests pass, and the output CSVs are byte-identical to pandas 3.0.6 / NumPy 2.5.3
- [x] CSVs are written with `\n` line endings on every OS, and `.gitattributes` keeps them LF in Git (protects MySQL `LOAD DATA`)

### SQL (executed on MySQL 8.0.46, strict mode + `ONLY_FULL_GROUP_BY`)
- [x] `schema.sql`, `data_quality.sql`, `sales_analysis.sql`, `business_queries.sql`: exit code 0, 0 errors
- [x] `LOAD DATA` with `--show-warnings`: 0 data warnings (no truncation)
- [x] Row counts: sales_raw 11,567 · fact_sales 11,461 · dim_date 1,461 · dim_customer 741 · dim_product 174 · dim_geography 36
- [x] Totals equal Python to the cent: sales 4,391,176.00 · profit 452,068.04 · 5,190 orders · Central margin 3.28% · Central effective discount 21.51%

### Numbers & documentation (checked by script)
- [x] Every headline number recomputed independently with plain pandas (not through `eda.py`) and compared with the docs; stale figures corrected (290 → 275 repaired values, 34.4% → 34.45%, 7 → 10 tests)
- [x] All DAX `Table[Column]` references match the CSV headers exactly; every `[Measure]` reference resolves to one of the 31 defined measures
- [x] All internal Markdown links and `#anchor` links resolve. The only exceptions are two intentional examples inside code blocks, pointing at screenshots you will add later
- [x] Placeholder/secret scan: no TODO/FIXME, no credentials, no machine-specific paths, no references to other projects
- [x] `.gitignore` tested in a scratch Git copy: 77 files staged; no `.venv`, `__pycache__`, `.env`, logs or sockets
- [x] All 13 charts inspected visually (titles, axis labels, no overlapping labels)
- [x] 6 dashboard **design mockups** rendered by `python src/dashboard_mockups.py` into `powerbi/mockups/`, from the real data. Each one was inspected visually, and each carries a "DESIGN MOCKUP – not a Power BI screenshot" banner. Their numbers match the validation tables

### Content completeness
- [x] Data dictionary, cleaning rationale, feature formulas, EDA with chart reasoning, 17 business questions, KPI definitions
- [x] Facts, hypotheses and recommendations separated; correlation never presented as causation; what-if labelled as an upper bound
- [x] Synthetic-data disclosure in README, data dictionary, reports, interview material and resume bullets
- [x] Beginner material: `START_HERE.md`, `docs/end_to_end_logic.md`, `powerbi/POWER_BI_STEP_BY_STEP.md` (concepts)
- [x] Power BI preparation: `POWER_BI_MASTER_GUIDE.md` (single build guide), `DAX_VALIDATION_CHECKLIST.md` (31 rows), `FINAL_VALIDATION.md` (4 levels, Actual column empty), `POWER_BI_TROUBLESHOOTING.md` (17 problems)
- [x] DAX identical (full text) across `DAX_Measures.md` and `POWER_BI_MASTER_GUIDE.md`; every expected value checked against values computed from the data
- [x] GitHub/profile text: `docs/GITHUB_PUBLISHING.md`, `docs/GITHUB_PROFILE_TEXT.md`; interview revision: `docs/INTERVIEW_MASTER_SHEET.md`
- [x] Interview material: `INTERVIEW_GUIDE.md` (90 Q&As), `docs/PLACEMENT_READINESS.md`, `docs/project_story.md`, `docs/resume_bullets.md`

## 🪟 Requires Power BI Desktop (you, on Windows)

> Not possible here: Power BI Desktop doesn't run on Linux. **No `.pbix` exists, the DAX has never been executed, and there are no dashboard screenshots.**

- [ ] Import the 5 CSVs, check the data types, confirm the row counts ([Master Guide Parts B–C](powerbi/POWER_BI_MASTER_GUIDE.md#part-b-create-the-power-bi-project))
- [ ] Create the 4 relationships; mark `DimDate` as the date table ([Parts D–E](powerbi/POWER_BI_MASTER_GUIDE.md#part-d-relationships))
- [ ] Create all 31 measures, with no formula errors
- [ ] Tick every row in [DAX_VALIDATION_CHECKLIST.md](powerbi/DAX_VALIDATION_CHECKLIST.md)
- [ ] Build the 5 pages + hidden Region Detail page ([Part G](powerbi/POWER_BI_MASTER_GUIDE.md#part-g-dashboard-pages))
- [ ] Complete [FINAL_VALIDATION.md](powerbi/FINAL_VALIDATION.md): all 29 rows *Pass*, *Actual* column filled in
- [ ] Save `powerbi/Regional_Sales_Dashboard.pbix`
- [ ] Export 5 screenshots to `screenshots/`; add the Executive Overview image to the README
- [ ] Update the README Power BI status line from "designed and specified" to "built and validated"

## 🐙 Requires GitHub (you)

Follow [docs/GITHUB_PUBLISHING.md](docs/GITHUB_PUBLISHING.md).
- [ ] Add your LinkedIn/GitHub links in the README *Author* section (there is a comment showing where)
- [ ] Create the empty public repository `regional-sales-performance-analysis`
- [ ] `git init` → `git add .` → check `git status` → commit → push
- [ ] Verify on GitHub: README, Mermaid diagram, charts and notebooks render; links work
- [ ] Add repository topics and pin the repository on your profile
- [ ] After the Power BI work: commit the `.pbix` and screenshots

## 💡 Optional improvements (not needed for the first release)

- [ ] Export the dashboard to PDF (`powerbi/Regional_Sales_Dashboard.pdf`) so it can be viewed without Power BI
- [ ] Save a PBIP version of the report for diff-friendly version control
- [ ] Run the pipeline on the real Superstore file and compare
- [ ] Add a GitHub Actions workflow that runs `pipeline.py` + `test_pipeline.py` on every push
- [ ] Add returns and shipping costs; a sales-targets fact table; RFM segmentation; a regional sales forecast
- [ ] Record a 2-minute video walkthrough of the dashboard for your profile
