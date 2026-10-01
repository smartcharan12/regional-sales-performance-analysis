-- =====================================================================
-- sales_analysis.sql  -  Core sales analysis, from basic to advanced
-- =====================================================================
-- Runs on the CLEAN star schema (see schema.sql).
-- Order of concepts: SELECT -> WHERE -> GROUP BY -> HAVING -> ORDER BY
--                    -> JOIN -> CASE -> CTE -> window functions
--
-- KEY RULE FOR RATIOS: margin = SUM(profit) / SUM(sales).
-- Never AVG(profit / sales): that gives a $5 sale the same weight as a
-- $5,000 sale.
-- =====================================================================
USE retailco;

-- =====================================================================
-- PART A - BASICS (single table)
-- =====================================================================

-- A1. Total sales, profit, margin, orders, quantity  (SELECT + aggregates)
-- COUNT(DISTINCT order_id) counts orders, not order lines.
SELECT
    ROUND(SUM(sales), 2)                        AS total_sales,
    ROUND(SUM(profit), 2)                       AS total_profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)    AS profit_margin_pct,
    COUNT(DISTINCT order_id)                    AS total_orders,
    SUM(quantity)                               AS total_quantity,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM fact_sales;

-- A2. Sales in 2024 only  (WHERE filters rows before aggregation)
SELECT ROUND(SUM(sales), 2) AS sales_2024
FROM fact_sales
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
-- Using a date RANGE instead of YEAR(order_date) = 2024 lets MySQL use
-- the index on order_date.

-- A3. Order lines that lost money, biggest losses first  (WHERE + ORDER BY + LIMIT)
SELECT order_id, product_id, sales, discount, profit
FROM fact_sales
WHERE profit < 0
ORDER BY profit ASC
LIMIT 10;

-- =====================================================================
-- PART B - JOINS AND GROUP BY
-- A JOIN combines rows from two tables where the key matches.
-- fact_sales holds the numbers; dim_geography holds the region names.
-- =====================================================================

-- B1. Sales, profit and margin by region
SELECT
    g.region,
    ROUND(SUM(f.sales), 2)                      AS sales,
    ROUND(SUM(f.profit), 2)                     AS profit,
    ROUND(SUM(f.profit) / SUM(f.sales) * 100, 2) AS profit_margin_pct,
    COUNT(DISTINCT f.order_id)                  AS orders
FROM fact_sales AS f
JOIN dim_geography AS g ON g.geo_key = f.geo_key
GROUP BY g.region
ORDER BY sales DESC;

-- B2. Monthly sales and profit (time trend)
SELECT
    d.yyyy_mm,
    ROUND(SUM(f.sales), 2)  AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM fact_sales AS f
JOIN dim_date AS d ON d.date_key = f.order_date_key
GROUP BY d.yyyy_mm
ORDER BY d.yyyy_mm;

-- B3. Category and sub-category performance
SELECT
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales), 2)                       AS sales,
    ROUND(SUM(f.profit), 2)                      AS profit,
    ROUND(SUM(f.profit) / SUM(f.sales) * 100, 2) AS profit_margin_pct
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_id = f.product_id
GROUP BY p.category, p.sub_category
ORDER BY p.category, profit DESC;

-- B4. Regions whose margin is below 10%  (HAVING filters GROUPS)
SELECT
    g.region,
    ROUND(SUM(f.profit) / SUM(f.sales) * 100, 2) AS profit_margin_pct
FROM fact_sales AS f
JOIN dim_geography AS g ON g.geo_key = f.geo_key
GROUP BY g.region
HAVING SUM(f.profit) / SUM(f.sales) * 100 < 10;

-- B5. Top 10 customers by sales (three-table join)
SELECT
    c.customer_name,
    c.segment,
    ROUND(SUM(f.sales), 2)  AS sales,
    ROUND(SUM(f.profit), 2) AS profit,
    COUNT(DISTINCT f.order_id) AS orders
FROM fact_sales AS f
JOIN dim_customer AS c ON c.customer_id = f.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment
ORDER BY sales DESC
LIMIT 10;

-- B6. Top 10 products by sales
SELECT
    p.product_name,
    p.sub_category,
    ROUND(SUM(f.sales), 2)  AS sales,
    ROUND(SUM(f.profit), 2) AS profit
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_id = f.product_id
GROUP BY p.product_id, p.product_name, p.sub_category
ORDER BY sales DESC
LIMIT 10;

-- =====================================================================
-- PART C - CASE: turning numbers into business categories
-- =====================================================================

-- C1. Profitability by discount band
SELECT
    CASE
        WHEN discount = 0    THEN '1. No discount'
        WHEN discount <= 0.2 THEN '2. 1-20%'
        WHEN discount <= 0.4 THEN '3. 21-40%'
        ELSE                      '4. Over 40%'
    END                                          AS discount_band,
    COUNT(*)                                     AS order_lines,
    ROUND(SUM(sales), 2)                         AS sales,
    ROUND(SUM(profit), 2)                        AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)     AS profit_margin_pct,
    ROUND(AVG(profit < 0) * 100, 1)              AS pct_lines_loss_making
FROM fact_sales
GROUP BY discount_band
ORDER BY discount_band;

-- =====================================================================
-- PART D - CTEs (WITH ...) : break a big query into named steps
-- =====================================================================

-- D1. Year-over-year sales growth (CTE + self-join on year - 1)
WITH yearly AS (
    SELECT d.year, SUM(f.sales) AS sales, SUM(f.profit) AS profit
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.order_date_key
    GROUP BY d.year
)
SELECT
    cur.year,
    ROUND(cur.sales, 2)                               AS sales,
    ROUND(prev.sales, 2)                              AS prev_year_sales,
    ROUND((cur.sales - prev.sales) / prev.sales * 100, 2)   AS yoy_sales_growth_pct,
    ROUND((cur.profit - prev.profit) / prev.profit * 100, 2) AS yoy_profit_growth_pct
FROM yearly AS cur
LEFT JOIN yearly AS prev ON prev.year = cur.year - 1
ORDER BY cur.year;
-- LEFT JOIN keeps the first year even though it has no previous year
-- (its growth shows as NULL rather than the row disappearing).

-- =====================================================================
-- PART E - WINDOW FUNCTIONS: calculations across related rows
-- without collapsing them (GROUP BY collapses, OVER() does not)
-- =====================================================================

-- E1. Same YoY growth with LAG() - shorter than the self-join
WITH yearly AS (
    SELECT d.year, SUM(f.sales) AS sales
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.order_date_key
    GROUP BY d.year
)
SELECT
    year,
    ROUND(sales, 2) AS sales,
    ROUND((sales - LAG(sales) OVER (ORDER BY year))
          / LAG(sales) OVER (ORDER BY year) * 100, 2) AS yoy_growth_pct
FROM yearly
ORDER BY year;

-- E2. Rank regions by profit margin (RANK)
SELECT
    region,
    ROUND(margin, 2) AS profit_margin_pct,
    RANK() OVER (ORDER BY margin DESC) AS margin_rank
FROM (
    SELECT g.region, SUM(f.profit) / SUM(f.sales) * 100 AS margin
    FROM fact_sales AS f
    JOIN dim_geography AS g ON g.geo_key = f.geo_key
    GROUP BY g.region
) AS r;

-- E3. Each region's share of company sales (window SUM over all rows)
SELECT
    region,
    ROUND(sales, 2) AS sales,
    ROUND(sales / SUM(sales) OVER () * 100, 2) AS sales_share_pct
FROM (
    SELECT g.region, SUM(f.sales) AS sales
    FROM fact_sales AS f
    JOIN dim_geography AS g ON g.geo_key = f.geo_key
    GROUP BY g.region
) AS r
ORDER BY sales DESC;

-- E4. Running total of sales within each year (cumulative / YTD)
WITH monthly AS (
    SELECT d.year, d.month_number, SUM(f.sales) AS sales
    FROM fact_sales AS f
    JOIN dim_date AS d ON d.date_key = f.order_date_key
    GROUP BY d.year, d.month_number
)
SELECT
    year,
    month_number,
    ROUND(sales, 2) AS sales,
    ROUND(SUM(sales) OVER (PARTITION BY year ORDER BY month_number), 2) AS ytd_sales
FROM monthly
ORDER BY year, month_number;
-- PARTITION BY year restarts the running total every January.
