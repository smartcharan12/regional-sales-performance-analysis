# Dashboard Mockups (not Power BI screenshots)

These six images are **design mockups** of the Power BI report, **rendered in Python (matplotlib)** by [`src/dashboard_mockups.py`](../../src/dashboard_mockups.py), using the project's real data (`data/processed/sales_cleaned.csv`).

| File | Page | Slicer state shown |
|---|---|---|
| `01_executive_overview_mockup.png` | Executive Overview | Year = 2024 |
| `02_regional_performance_mockup.png` | Regional Performance | All years |
| `03_product_performance_mockup.png` | Product Performance | All years |
| `04_customer_performance_mockup.png` | Customer Performance | All years |
| `05_profitability_discount_mockup.png` | Profitability & Discount | All years |
| `06_region_detail_central_mockup.png` | Region Detail (hidden drill-through), Central | All years |

## What they are for
* **Preview the layout** of [Dashboard_Design.md](../Dashboard_Design.md) before building it.
* **Visual reference while building:** your Power BI page should show the same numbers (they match [DAX_VALIDATION_CHECKLIST.md](../DAX_VALIDATION_CHECKLIST.md) and the per-page validation tables).
* Give GitHub visitors an idea of the dashboard until the real report exists.

## What they are not
* **Not Power BI screenshots.** Power BI Desktop is Windows-only and wasn't available when the project was built. Every image carries a visible **DESIGN MOCKUP** tag and banner.
* Not proof that the DAX works. That proof comes from [FINAL_VALIDATION.md](../FINAL_VALIDATION.md).
* Some details necessarily differ from Power BI: the filled map is drawn as a state bar chart, and fonts, spacing and interactivity are different.

Real screenshots of the finished `.pbix` go in [`screenshots/`](../../screenshots/), with different file names, so the two can never be confused.

## Regenerate
```bash
python src/dashboard_mockups.py      # needs data/processed/sales_cleaned.csv (run src/pipeline.py first)
```
