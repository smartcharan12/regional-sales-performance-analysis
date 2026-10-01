# Executive Summary: Regional Sales Performance, RetailCo 2021–2024

### Business problem
Sales grew in 2024, but profit fell, and leadership could not see why. Management needed a region-by-region view of **profitability**, not just revenue, and a clear list of where money is being lost.

### Dataset
11,567 order-line records in a synthetic, Superstore-style sales export (Jan 2021 – Dec 2024). After cleaning: **11,461 lines, 5,190 orders, 741 customers, 174 products, 4 regions**. Cleaning repaired 275 values, removed 70 exact duplicates and removed 36 records that could not be trusted (0.3%). *Because the data is synthetic, the findings illustrate the method and are not claims about a real company.*

### Methodology
Python (cleaning, validation, EDA) → MySQL star schema (independent verification: every total matches Python to the cent) → Power BI model with DAX measures and a 5-page dashboard (specified; build and validation in Power BI Desktop pending).

### Key findings

| | |
|---|---|
| **Overall** | $4.39M sales · $452K profit · **10.3% margin** |
| **2024** | Sales **+6.7%**, profit **−6.6%**, margin down to **9.2%** (lowest in 4 years) |

**Regional performance**
* **West** is the largest region: $1.51M sales, $186K profit, growing +14%/yr.
* **East** is the most efficient: 13.2% margin, growing +12%/yr.
* **Central** is the profit problem: 20% of sales but 6% of profit (**3.3% margin**, a loss in 2024). Its effective discount is 21.5% vs ~13.5% in East/West.
* **South** is the volume problem: sales down **12% per year**, although its 10% margin is healthy.

**Product performance**
* Technology is the largest category ($1.82M sales, $253K profit). Office Supplies has the best margin (18%).
* **Tables (−$91.5K) and Bookcases (−$30.4K) lose money in every region**, leaving Furniture break-even on $1.45M of sales.

**Profitability**
* Every discount level of **30% or more is loss-making**: −$249K in total.
* Margin falls from 25% with no discount to 6% at a 20% discount.

### Recommendations

| Priority | Action | Owner | KPI to monitor |
|---|---|---|---|
| 1 | Manager approval for discounts ≥ 30%; **pilot in Central** for one quarter | Sales Director, Central RM | Effective discount %, Central margin, order volume |
| 2 | Re-price / renegotiate costs for Tables and Bookcases; end deep promotions on them | Category Manager, Procurement | Sub-category margin |
| 3 | Add margin to sales targets and incentives | CFO, HR | Profit growth vs sales growth (Growth Gap) |
| 4 | Customer-retention review in South before any promotional spend | South RM | South YoY sales, active customers |
| 5 | Protect West/East service and stock ahead of the Sep–Dec peak | Operations | Monthly sales vs seasonal baseline |

### Expected business impact
* **Upper bound:** if 30%+ discounts had been 20% with unchanged volume, profit would have been up to **$264K higher** (margin 10.3% → 15.4%). Real impact will be lower because some customers will buy less. The Central pilot will measure by how much.
* Restoring Central to the margin of the other regions on its normal-discount business is the single largest lever.
* Removing the Tables/Bookcases loss would add up to ~$122K over four years at current volumes.

*Details: [Business_Insights.md](Business_Insights.md) · Dashboard spec: [Dashboard_Design.md](../powerbi/Dashboard_Design.md) · Analysis: [notebook 04](../notebooks/04_business_analysis.ipynb)*
