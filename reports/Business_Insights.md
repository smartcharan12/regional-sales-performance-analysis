# Business Insights

Each insight follows the same structure, so facts are never mixed up with opinions:

* 📊 **Observed fact**: measured directly in the data (reproducible in notebook 04 and in SQL).
* 💭 **Possible explanation**: a hypothesis that fits the facts but is **not proven** by this data.
* 🔍 **What to investigate**: the evidence needed to confirm or reject the explanation.
* ✅ **Action to consider**: a recommendation, with the KPI that would show whether it worked.

> Correlation is not causation. Where two things move together (e.g. discount and margin), this report says "associated with", not "caused by", unless the mechanism is arithmetic.

> The data is synthetic (documented in [data dictionary](../docs/data_dictionary.md#why-synthetic-data)), so these insights demonstrate the analytical method.

---

## Insight 1: 2024 growth was not profitable

📊 **Fact**
* Sales rose **+6.7%** ($1.118M → $1.193M) while profit fell **−6.6%** ($118.1K → $110.2K).
* Margin dropped from 10.6% to **9.2%**, the lowest in four years.
* Effective discount rose from 15.6% to 16.2%. Losses on lines discounted ≥ 30% grew from −$63K to −$81K.
* The largest profit drops came from Central (−$8.4K) and from Tables (−$6.9K), even though Tables *sales* increased.

💭 **Possible explanation:** part of the 2024 growth was "bought" with deeper discounts. Selling more of a loss-making product (Tables) increases the total loss.

🔍 **Investigate:** were 2024 sales targets or incentives revenue-based? Were there promotions or competitor price cuts in 2024?

✅ **Action:** report profit growth next to sales growth on every dashboard page. Add the *Growth Gap* KPI (profit growth − sales growth; 2024 = −13.3 pp) as an early-warning signal.

---

## Insight 2: Central's low margin is associated with discounting, not with what it sells

📊 **Fact**
* Central: 20% of company sales but only 6% of profit; margin **3.3%** vs 10.3% for the company. In 2024 Central made a **loss** (−$744).
* Central's effective discount is **21.5%** vs 13.5% in East and West. 28% of Central's lines carry 30%+ discounts (vs 11–15% elsewhere).
* Central has the highest effective discount in **15 of 17 sub-categories**, so it discounts more *on the same products*.
* On lines discounted under 30%, Central's margin (17.4%) is close to the other regions' (18.0%). Its 30%+ lines lose −$96K.

💭 **Possible explanation:** Central's sales teams may have more pricing freedom, be paid on revenue, or face stronger local competition. The data shows *what* happens, not *why*.

🔍 **Investigate:** Central's discount approval rules and sales incentive plans; which customers and sales reps account for most 30%+ discounts; competitor pricing in Texas and Illinois.

✅ **Action:** require manager approval for discounts ≥ 30%, **piloted in Central first**. Compare Central's margin and volume with the other regions over 2–3 months (KPI: Central effective discount %, Central margin, Central order count).

---

## Insight 3: Tables and Bookcases lose money everywhere

📊 **Fact**
* Tables: $393K sales, **−$91.5K profit (−23.3%)**. Bookcases: $234K sales, **−$30.4K (−13.0%)**.
* Both lose money in **all four regions**, which makes this a product problem and not just a regional one.
* Even *without* discount, Tables make only ~8% margin, and they already lose money at ordinary 10–20% discounts.
* As a result, the Furniture category is break-even (−0.1%) on $1.45M of sales.

💭 **Possible explanation:** the list price is too low relative to supplier cost for these bulky items, and they are frequently cleared at deep discounts (Tables' effective discount is 25.6%, vs 15.5% for the company).

🔍 **Investigate:** supplier costs, freight/handling costs (not in the data, so the true loss may be larger), and whether table sales drive profitable add-on purchases such as chairs in the same order.

✅ **Action:** Category Manager and Procurement to review pricing and supplier terms; stop deep promotions on Tables/Bookcases; set a minimum margin floor (KPI: sub-category margin).

---

## Insight 4: Deep discounts are consistently loss-making

📊 **Fact**
* Margin by discount: 24.9% (0%) → 16.5% (10%) → 5.8% (20%) → **−7.7% (30%)** → −29.8% (40%) → worse beyond.
* Every discount level of **30% or more** loses money in total: −$249K across 1,844 lines (10.6% of sales).
* Correlation between discount and line margin: −0.81.

💭 **Explanation (mechanism, not just correlation):** a discount lowers the price while the cost of goods stays the same, so beyond the product's gross margin every extra point of discount is a direct loss. What the data *cannot* tell us is how many of those sales would have happened at a lower discount.

🔍 **Investigate:** price sensitivity, using a controlled test (cap discounts in one area, compare with a similar area).

✅ **Action / sizing:** if all 30%+ lines had been sold at 20% with **unchanged volume**, profit would be up to **$264K higher** (margin 10.3% → 15.4%). This is an **upper bound**, not a forecast, because some customers would buy less. Even capturing a third of it would add ≈ $88K.

---

## Insight 5: South is shrinking, but it is not unprofitable

📊 **Fact:** South's sales fell every year (CAGR **−12.2%**, $243K → $164K), while its margin stays healthy at ~10%.

💭 **Possible explanation:** lost customers, weaker sales coverage, or a competitor entering the market. This is a **volume** problem, not a price problem, so discounting more would be the wrong fix.

🔍 **Investigate:** customer counts and churn in the South by year; win/loss data from the sales team; local market trends.

✅ **Action:** Regional Manager South to run a customer-retention review before any promotional spending (KPI: South YoY sales, active customers).

---

## Insight 6: West and East drive all of the growth

📊 **Fact:** West (+14.0%/yr) and East (+12.3%/yr) are growing with healthy margins of 12–13%, and together make up 62% of sales and 76% of profit.

✅ **Action:** protect these regions' service levels and stock, especially before the Sep–Dec peak (Q4 ≈ 37% of annual sales).

---

## Insight 7: Revenue is concentrated in a minority of customers

📊 **Fact:** the top 20% of customers produce **54%** of sales. Some large customers are barely profitable (e.g. $41.7K sales at a 1.1% margin).

✅ **Action:** a key-account programme for the top ~150 customers that is priced on **margin**, not volume (KPI: top-customer retention and margin).

---

## What this analysis cannot tell us (limitations)

* **Costs** beyond cost of goods (shipping, returns, overheads) are not in the data.
* **Causation:** the reasons behind discounting behaviour need interviews and/or experiments.
* **Price elasticity:** the what-if assumes unchanged volume.
* **Synthetic data:** patterns come from documented generator rules.

➡ The one-page version for leadership is in [Executive_Summary.md](Executive_Summary.md).
