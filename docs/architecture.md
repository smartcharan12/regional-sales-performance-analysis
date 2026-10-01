# Project Architecture

## The pipeline at a glance

```mermaid
flowchart TD
    A["Raw sales export<br/>data/raw/sales_raw.csv<br/>11,567 rows, with errors"] --> B["1. Data understanding<br/>notebook 01"]
    B --> C["2. Data quality assessment<br/>notebook 01 + sql/data_quality.sql"]
    C --> D["3. Data cleaning<br/>src/data_cleaning.py · notebook 02"]
    D --> E["4. Feature engineering<br/>src/feature_engineering.py"]
    E --> F["Clean dataset<br/>data/processed/sales_cleaned.csv<br/>11,461 rows · 32 columns"]
    F --> G["5. EDA<br/>src/eda.py · notebook 03 · visualizations/"]
    F --> H["6. Star schema export<br/>src/build_star_schema.py"]
    H --> I["SQL database (MySQL 8)<br/>sql/*.sql"]
    H --> J["Power BI data model<br/>powerbi/Data_Model.md"]
    G --> K["7. Business questions & KPIs<br/>notebook 04"]
    I --> K
    J --> L["8. DAX measures<br/>powerbi/DAX_Measures.md"]
    L --> M["9. Interactive dashboard<br/>powerbi/Dashboard_Design.md"]
    K --> N["10. Insights<br/>reports/Business_Insights.md"]
    M --> N
    N --> O["11. Recommendations<br/>reports/Executive_Summary.md"]
```

**One command reproduces everything from raw data to charts:**

```bash
python src/pipeline.py --regenerate   # generate -> clean -> features -> star schema -> charts
python tests/test_pipeline.py         # prove the cleaning is correct
```

---

## What each stage does and why

The stage-by-stage explanation (what enters, what happens, what comes out, why the stage exists, and how the next stage uses it) is in **[end_to_end_logic.md](end_to_end_logic.md)**. It follows one real order line from the raw file to the final recommendation. This page covers only the technical layout.

---

## Code modules

| Module | Responsibility | Used by |
|---|---|---|
| `src/utils.py` | Paths, reference data (valid regions, State→Region), chart style | everything |
| `src/generate_data.py` | Builds the synthetic raw dataset | pipeline, tests |
| `src/data_cleaning.py` | Cleaning steps + log + validation | notebook 02, pipeline, tests |
| `src/feature_engineering.py` | Derived columns, weighted margin helper | notebook 02, pipeline |
| `src/eda.py` | Summary tables + chart functions | notebooks 03/04, pipeline |
| `src/build_star_schema.py` | Fact/dimension split + integrity checks | pipeline, tests |
| `src/pipeline.py` | Runs everything in order | command line |
| `src/dashboard_mockups.py` | Renders Python design mockups of the 5 Power BI pages + Region Detail (not screenshots) | command line |
| `tests/test_pipeline.py` | Proves cleaning against ground truth | command line / pytest |

**Why modules *and* notebooks?** Notebooks are for explaining and exploring. Modules are for logic that must be correct, reusable and testable. The notebooks import the modules, so explanation and pipeline code can never drift apart.

---

## Verification built into the architecture

| Check | Where | What it proves |
|---|---|---|
| 10 automated tests | `tests/test_pipeline.py` | Cleaning recovers the true values; no rows invented; headline numbers unchanged |
| Python vs SQL reconciliation | `sql/*.sql` on MySQL 8 | Two engines give identical totals to the cent |
| DAX expected values | `powerbi/DAX_VALIDATION_CHECKLIST.md` | What each measure must show in Power BI *(Power BI Desktop validation required)* |
