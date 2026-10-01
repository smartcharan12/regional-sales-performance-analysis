-- =====================================================================
-- business_queries.sql  -  Answers to the management questions (MySQL 8)
-- =====================================================================
-- Each query answers one question from reports/Business_Insights.md.
-- They use the v_sales view (star schema joined back together) to keep
-- the business logic easy to read.
-- =====================================================================
USE retailco;

-- ---------------------------------------------------------------------
-- BQ1. Which regions are growing or declining?
-- Sales per region per year, plus YoY growth using LAG partitioned by
-- region (so 2024 is compared with 2023 OF THE SAME REGION).
-- ---------------------------------------------------------------------
WITH region_year AS (
    SELECT region, year, SUM(sales) AS sales, SUM(profit) AS profit
    FROM v_sales
    GROUP BY region, year
)
SELECT
    region,
    year,
    ROUND(sales, 2)  AS sales,
    ROUND(profit, 2) AS profit,
    ROUND((sales - LAG(sales) OVER w) / LAG(sales) OVER w * 100, 2) AS yoy_sales_growth_pct
FROM region_year
WINDOW w AS (PARTITION BY region ORDER BY year)
ORDER BY region, year;

-- ---------------------------------------------------------------------
-- BQ2. Sales went up in 2024 - did profit? (detect "growth without profit")
-- ---------------------------------------------------------------------
WITH yearly AS (
    SELECT year,
           SUM(sales)  AS sales,
           SUM(profit) AS profit,
           SUM(discount_amount) / SUM(gross_sales) * 100 AS effective_discount_pct
    FROM v_sales
    GROUP BY year
)
SELECT
    year,
    ROUND(sales, 2)                                         AS sales,
    ROUND(profit, 2)                                        AS profit,
    ROUND(profit / sales * 100, 2)                          AS profit_margin_pct,
    ROUND(effective_discount_pct, 2)                        AS effective_discount_pct,
    ROUND((sales  / LAG(sales)  OVER (ORDER BY year) - 1) * 100, 2) AS yoy_sales_pct,
    ROUND((profit / LAG(profit) OVER (ORDER BY year) - 1) * 100, 2) AS yoy_profit_pct
FROM yearly
ORDER BY year;

-- ---------------------------------------------------------------------
-- BQ3. Loss-making products (total profit < 0 over the whole period)
-- ---------------------------------------------------------------------
SELECT
    product_name,
    sub_category,
    ROUND(SUM(sales), 2)                            AS sales,
    ROUND(SUM(profit), 2)                           AS profit,
    ROUND(SUM(discount_amount) / SUM(gross_sales) * 100, 1) AS effective_discount_pct
FROM v_sales
GROUP BY product_id, product_name, sub_category
HAVING SUM(profit) < 0
ORDER BY profit ASC;

-- ---------------------------------------------------------------------
-- BQ4. High sales but low profit: products in the top 25% by sales
-- (NTILE(4) splits products into 4 equal groups by sales) with a margin
-- below 5%.
-- ---------------------------------------------------------------------
WITH product_perf AS (
    SELECT
        product_id,
        product_name,
        SUM(sales)  AS sales,
        SUM(profit) AS profit,
        NTILE(4) OVER (ORDER BY SUM(sales) DESC) AS sales_quartile
    FROM v_sales
    GROUP BY product_id, product_name
)
SELECT
    product_name,
    ROUND(sales, 2)                 AS sales,
    ROUND(profit, 2)                AS profit,
    ROUND(profit / sales * 100, 2)  AS profit_margin_pct
FROM product_perf
WHERE sales_quartile = 1
  AND profit / sales * 100 < 5
ORDER BY profit;
-- Note: NTILE and the pandas quantile() method split the boundary a
-- little differently, so the edge of the list can differ by a product.

-- ---------------------------------------------------------------------
-- BQ5. Where exactly is profit lost? Region x Sub-Category matrix,
-- showing only the loss-making combinations.
-- ---------------------------------------------------------------------
SELECT
    region,
    sub_category,
    ROUND(SUM(sales), 2)                                    AS sales,
    ROUND(SUM(profit), 2)                                   AS profit,
    ROUND(SUM(discount_amount) / SUM(gross_sales) * 100, 1) AS effective_discount_pct
FROM v_sales
GROUP BY region, sub_category
HAVING SUM(profit) < 0
ORDER BY profit;

-- ---------------------------------------------------------------------
-- BQ6. Is Central discounting more than other regions?
-- Effective discount % = discount given away / list-price value.
-- Share of lines with a deep (>= 30%) discount.
-- ---------------------------------------------------------------------
SELECT
    region,
    ROUND(SUM(discount_amount) / SUM(gross_sales) * 100, 2) AS effective_discount_pct,
    ROUND(AVG(discount >= 0.3) * 100, 1)                    AS pct_lines_deep_discount,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)                AS profit_margin_pct
FROM v_sales
GROUP BY region
ORDER BY effective_discount_pct DESC;

-- ---------------------------------------------------------------------
-- BQ7. Customer concentration: what share of sales comes from the top
-- 10% of customers? (window functions over customer totals)
-- ---------------------------------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS sales
    FROM v_sales
    GROUP BY customer_id
),
ranked AS (
    SELECT
        customer_id,
        sales,
        ROW_NUMBER() OVER (ORDER BY sales DESC) AS rn,
        COUNT(*)     OVER ()                    AS n_customers,
        SUM(sales)   OVER ()                    AS total_sales
    FROM customer_sales
)
SELECT
    ROUND(SUM(CASE WHEN rn <= FLOOR(n_customers * 0.10) THEN sales END)
          / MAX(total_sales) * 100, 2) AS top_10pct_customer_share,
    ROUND(SUM(CASE WHEN rn <= FLOOR(n_customers * 0.20) THEN sales END)
          / MAX(total_sales) * 100, 2) AS top_20pct_customer_share
FROM ranked;

-- ---------------------------------------------------------------------
-- BQ8. Best and worst sub-category inside each region
-- (DENSE_RANK partitioned by region)
-- ---------------------------------------------------------------------
WITH region_sub AS (
    SELECT region, sub_category, SUM(profit) AS profit
    FROM v_sales
    GROUP BY region, sub_category
),
ranked AS (
    SELECT
        region,
        sub_category,
        profit,
        DENSE_RANK() OVER (PARTITION BY region ORDER BY profit DESC) AS best_rank,
        DENSE_RANK() OVER (PARTITION BY region ORDER BY profit ASC)  AS worst_rank
    FROM region_sub
)
SELECT region,
       sub_category,
       ROUND(profit, 2) AS profit,
       CASE WHEN best_rank = 1 THEN 'Most profitable' ELSE 'Least profitable' END AS position
FROM ranked
WHERE best_rank = 1 OR worst_rank = 1
ORDER BY region, profit DESC;

-- ---------------------------------------------------------------------
-- BQ9. Seasonality: average sales per calendar month across years
-- ---------------------------------------------------------------------
WITH monthly AS (
    SELECT year, month_number, SUM(sales) AS sales
    FROM v_sales
    GROUP BY year, month_number
)
SELECT
    month_number,
    ROUND(AVG(sales), 2) AS avg_monthly_sales,
    ROUND(AVG(sales) / AVG(AVG(sales)) OVER () * 100, 1) AS index_vs_average
FROM monthly
GROUP BY month_number
ORDER BY month_number;

-- ---------------------------------------------------------------------
-- BQ10. Segment performance
-- ---------------------------------------------------------------------
SELECT
    segment,
    ROUND(SUM(sales), 2)                         AS sales,
    ROUND(SUM(sales) / SUM(SUM(sales)) OVER () * 100, 2) AS sales_share_pct,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)     AS profit_margin_pct,
    COUNT(DISTINCT customer_id)                  AS customers
FROM v_sales
GROUP BY segment
ORDER BY sales DESC;
