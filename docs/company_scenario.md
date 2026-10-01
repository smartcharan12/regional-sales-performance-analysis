# Business Scenario: RetailCo

> RetailCo is **fictional**. The scenario frames the project the way a real analyst assignment would arrive.

## The company

RetailCo sells **office furniture, office supplies and technology** to consumers, corporate clients and home-office customers across the United States. Sales are managed in **four regions**: West, East, Central and South. Each region has a regional manager who controls local pricing and discount approvals.

## The assignment (as it arrived)

> *From: Head of Sales*
> *To: Data Analyst*
>
> "We've grown sales again this year, but Finance says profit is down and nobody can tell me why. I need to understand how each region is really performing — not just revenue — and where we're losing money. Can you analyse the last four years of order data and build us a dashboard we can keep using? I'd like recommendations for the leadership meeting."

**What this tells the analyst:**
* The real concern is **profitability**, not sales. The analysis must always show margin next to revenue.
* The output must be **reusable**: a dashboard, not a one-off spreadsheet.
* Leadership needs **actions**, so findings have to end in recommendations with owners.

## Stakeholders

| Stakeholder | What they care about | Dashboard element that answers it | Action they might take |
|---|---|---|---|
| **CEO** | "Are we growing profitably? What are the 2–3 things to fix?" | Page 1 KPI cards: Sales YoY **+6.7%** vs Profit YoY **−6.6%**; `Growth Gap` card | Commission a discount-policy review; ask Finance to set margin targets alongside sales targets |
| **Sales Manager** (national) | "Which regions and customers drive revenue? Are we hitting growth?" | Page 2 regional ranking and yearly trend; Page 4 top customers | Shift sales effort to growing West/East; start a key-account programme for the top 20% of customers (54% of sales) |
| **Regional Manager: Central** | "Why is my region's profit so low when sales are fine?" | Page 2 margin vs company (3.3% vs 10.3%); Page 5 effective discount by region (21.5%) and profitability matrix | Introduce approval for discounts ≥ 30%; review which accounts and sub-categories get deep discounts |
| **Regional Manager: South** | "Why are we shrinking?" | Page 2 yearly sales by region (South CAGR −12.2%) | Investigate lost customers and competitor activity before spending on promotions (South's margin is healthy, so the problem is volume, not price) |
| **Finance Manager** | "Where exactly is profit leaking, and how much is at stake?" | Page 5: deep-discount loss (−$249K), what-if uplift (≤ $264K), loss-making products | Model a discount cap; build margin into the budget; review Tables/Bookcases costs with Procurement |
| **Category Manager** | "Which products should we re-price, promote or drop?" | Page 3: profit by sub-category; high-sales/low-margin list (8 products) | Re-price or renegotiate supplier cost for Tables and Bookcases; stop promoting them with deep discounts |

## Success criteria for the project

1. Every stakeholder above can answer their question from the dashboard in under a minute.
2. Python and SQL totals reconcile exactly (verified: $4,391,176.00 sales, 5,190 orders), and the dashboard must show the same values (checked in Power BI Desktop with `powerbi/DAX_VALIDATION_CHECKLIST.md`).
3. Each recommendation has an owner and a KPI to monitor it.
4. The pipeline can be re-run on next quarter's export with one command.
