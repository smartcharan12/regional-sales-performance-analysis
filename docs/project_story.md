# The Project Story

*Read this aloud a few times. It's meant to sound like you talking, not like a textbook. Use your own words in the interview; the point is to know the story so well that the order comes naturally.*

---

**The situation.**
I wanted a project that looks like a real analyst assignment, not a tutorial. So I set it up the way it usually arrives: a retailer, I called it RetailCo, grew its sales in 2024, but its profit went *down*, and nobody could explain why. Their reports only showed revenue. My job was to find out where the money was going and give management something they could act on.

**The data, and why I made my own.**
I couldn't use real company data, since that's confidential, and the usual public sample, Superstore, is already clean, so there's nothing to really clean. So I wrote a generator in Python. It produces about 11,500 order lines over four years in the Superstore format. The business patterns come from rules I wrote down, and it deliberately adds the kind of mess real exports have: duplicate rows, "east" vs "East", prices stored as text like "$1,277.10", blank regions, dates like 30 February. The big advantage is that I kept the clean version, so later I could *prove* my cleaning worked rather than just hope it did.

**Getting to know the data.**
Before changing anything, I looked. The most important thing I learned early was what one row means: one product on one order. That sounds small, but it means the same Order ID repeating is completely normal. If I'd treated those as duplicates, I would have deleted real sales.

**Cleaning: fix before you delete.**
My rule was to repair what can be repaired and delete only what can't be trusted. A sale in Houston with a blank region isn't useless: Texas is always in the Central region, and I checked that rule against the data before relying on it. So I filled it in. "$1,277.10" became the number 1277.10. A discount typed as 20 became 0.20, because 20% is a valid discount level. But a sale with no amount at all? I couldn't rebuild that without inventing money, so it went. In the end I removed 106 rows, 70 of them exact duplicates, repaired 275 values, and logged every step. Ten automated tests compare my result with the clean original.

**What the data showed.**
The headline came quickly: in 2024, sales were up 6.7% but profit was down 6.6%. Then I asked *where*. By region, the Central region stood out: decent sales, but it kept only about 3 cents of every dollar, against 13 in the East. By product, Tables and Bookcases lost money in every single region. And when I grouped sales by discount level, there was a clear line: up to 20% discount still made money, but every level from 30% upward lost money overall, about $249K in total.

**Not jumping to conclusions.**
For Central there were two possible explanations: either it sells different, less profitable products, or it simply discounts more. So I tested both. Central gave the deepest discounts in 15 of the 17 product groups. And on its normally discounted sales, its margin was about the same as everyone else's. So the evidence points to discounting, not product mix. I'm careful to call that an association: *why* Central discounts more, whether that's incentives, approval rules or competition, is something you'd have to ask the business.

**Making sure the numbers are right.**
I loaded the data into a MySQL database as a star schema, one table of sales linked to tables of customers, products, places and dates, and re-ran the key questions in SQL. The totals matched Python to the cent. I also have a test that pins the headline numbers, so the documentation can't drift away from the data.

**Making it usable.**
Managers don't run notebooks, so I designed a Power BI report: the same star schema, about 30 DAX measures (things like profit margin and year-over-year growth that recalculate for whatever you click), and five pages, one per audience. That runs from the CEO's overview to a page that shows exactly where profit leaks. For every measure I wrote down the value it should show, so the report can be checked as it's built. *(Building and validating the `.pbix` in Power BI Desktop is the last step. Only say "I built it" once you have.)*

**What I recommended.**
Don't ban discounts. Instead, require manager approval for discounts of 30% or more, and pilot that in Central first, measuring both margin and order volume against the other regions. I estimated the upside at up to about $264K. That's an upper bound, because some customers would buy less at a higher price, and measuring exactly that is the point of the pilot. I also recommended a pricing review for Tables and Bookcases, adding margin to sales targets, and looking into why the South region keeps losing volume.

**What I'd do with real data.**
Point the same pipeline at the company's database, re-run the quality checks (real data always has surprises), add shipping and returns costs, and talk to the regional managers before finalising anything.

**The one-line takeaway.**
Sales growth isn't the same as profit growth. Here, discounting quietly ate the gains, and the project shows how I'd find that, prove it, and turn it into a decision.
