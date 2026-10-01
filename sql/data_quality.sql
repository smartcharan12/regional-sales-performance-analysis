-- =====================================================================
-- data_quality.sql  -  Find problems in the RAW data using SQL (MySQL 8)
-- =====================================================================
-- These queries reproduce, in SQL, the checks done in
-- notebooks/02_data_cleaning.ipynb. In a real company the raw data often
-- lives in a database, so an analyst must be able to profile it with SQL
-- before any Python is involved.
--
-- All checks run on sales_raw (every column is text).
-- =====================================================================
USE retailco;

-- ---------------------------------------------------------------------
-- Q1. How many rows did we receive?
-- COUNT(*) counts rows. This is the "before" number for cleaning.
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS raw_rows
FROM sales_raw;

-- ---------------------------------------------------------------------
-- Q2. Missing values per important column.
-- In a text table, "missing" can be NULL or an empty string ''.
-- SUM(condition) counts the rows where the condition is TRUE, because
-- MySQL treats TRUE as 1 and FALSE as 0.
-- ---------------------------------------------------------------------
SELECT
    SUM(region        IS NULL OR region        = '') AS missing_region,
    SUM(customer_name IS NULL OR customer_name = '') AS missing_customer_name,
    SUM(product_name  IS NULL OR product_name  = '') AS missing_product_name,
    SUM(sales         IS NULL OR sales         = '') AS missing_sales,
    SUM(profit        IS NULL OR profit        = '') AS missing_profit,
    SUM(order_date    IS NULL OR order_date    = '') AS missing_order_date
FROM sales_raw;

-- ---------------------------------------------------------------------
-- Q3. Exact duplicate rows.
-- GROUP BY every column puts identical rows in the same group;
-- HAVING COUNT(*) > 1 keeps only groups that appear more than once.
-- (WHERE filters rows BEFORE grouping; HAVING filters groups AFTER.)
-- ---------------------------------------------------------------------
SELECT COUNT(*)                AS duplicated_groups,
       SUM(copies - 1)         AS extra_rows_to_remove
FROM (
    SELECT COUNT(*) AS copies
    FROM sales_raw
    GROUP BY order_id, order_date, ship_date, ship_mode, customer_id,
             customer_name, segment, country, city, state, region,
             product_id, category, sub_category, product_name,
             sales, quantity, discount, profit
    HAVING COUNT(*) > 1
) AS dup;

-- ---------------------------------------------------------------------
-- Q4. Repeated Order IDs are NORMAL (one order, many products).
-- This query proves it: most orders contain more than one line.
-- ---------------------------------------------------------------------
SELECT lines_per_order, COUNT(*) AS orders
FROM (
    SELECT order_id, COUNT(DISTINCT product_id) AS lines_per_order
    FROM sales_raw
    GROUP BY order_id
) AS t
GROUP BY lines_per_order
ORDER BY lines_per_order;

-- ---------------------------------------------------------------------
-- Q5. Inconsistent spelling of Region and Category.
-- Anything other than the 4 regions / 3 categories is a problem.
-- BINARY makes the comparison case-sensitive ('east' <> 'East').
-- ---------------------------------------------------------------------
SELECT region, COUNT(*) AS row_count
FROM sales_raw
WHERE region IS NULL
   OR BINARY region NOT IN ('Central', 'East', 'South', 'West')
GROUP BY region
ORDER BY row_count DESC;

SELECT category, COUNT(*) AS row_count
FROM sales_raw
WHERE BINARY category NOT IN ('Furniture', 'Office Supplies', 'Technology')
GROUP BY category
ORDER BY row_count DESC;

-- ---------------------------------------------------------------------
-- Q6. Leading / trailing spaces.
-- TRIM() removes them; if the trimmed value differs, spaces existed.
-- ---------------------------------------------------------------------
SELECT 'city' AS column_name, COUNT(*) AS rows_with_spaces
FROM sales_raw WHERE city <> TRIM(city)
UNION ALL
SELECT 'region', COUNT(*) FROM sales_raw WHERE region <> TRIM(region)
UNION ALL
SELECT 'category', COUNT(*) FROM sales_raw WHERE category <> TRIM(category);

-- ---------------------------------------------------------------------
-- Q7. Sales stored as text with '$' or ','  (cannot be summed as-is)
-- ---------------------------------------------------------------------
SELECT sales
FROM sales_raw
WHERE sales LIKE '%$%' OR sales LIKE '%,%'
LIMIT 10;

-- ---------------------------------------------------------------------
-- Q8. Impossible numbers: Sales <= 0, Quantity <= 0, Discount > 1.
-- CAST converts text to a number. REPLACE strips '$' and ',' first.
-- A CASE expression labels each problem type.
-- ---------------------------------------------------------------------
SELECT issue, COUNT(*) AS row_count
FROM (
    SELECT CASE
             WHEN CAST(REPLACE(REPLACE(sales, '$', ''), ',', '') AS DECIMAL(12,2)) <= 0
                  THEN 'Sales <= 0'
             WHEN CAST(quantity AS SIGNED) <= 0
                  THEN 'Quantity <= 0'
             WHEN CAST(discount AS DECIMAL(6,2)) > 1
                  THEN 'Discount > 1 (typed as %)'
             ELSE 'OK'
           END AS issue
    FROM sales_raw
    WHERE sales <> '' AND quantity <> '' AND discount <> ''
) AS checks
WHERE issue <> 'OK'
GROUP BY issue;

-- ---------------------------------------------------------------------
-- Q9. Invalid dates.
-- STR_TO_DATE returns NULL when the text is not a real date
-- (e.g. '2023-02-30' or 'not recorded').
-- ---------------------------------------------------------------------
SELECT order_date, COUNT(*) AS row_count
FROM sales_raw
WHERE STR_TO_DATE(order_date, '%Y-%m-%d') IS NULL
GROUP BY order_date;

-- Ship date earlier than order date (impossible)
SELECT COUNT(*) AS ship_before_order
FROM sales_raw
WHERE STR_TO_DATE(ship_date, '%Y-%m-%d') < STR_TO_DATE(order_date, '%Y-%m-%d');

-- ---------------------------------------------------------------------
-- Q10. Does every State map to a single Region? (justifies rebuilding
-- missing Region values from State during cleaning)
-- ---------------------------------------------------------------------
SELECT state,
       COUNT(DISTINCT TRIM(LOWER(region))) AS distinct_regions
FROM sales_raw
WHERE region IS NOT NULL AND region <> ''
GROUP BY state
HAVING COUNT(DISTINCT TRIM(LOWER(region))) > 1;
-- Rows returned here are only spelling variants such as 'centrl',
-- which confirms each state belongs to exactly one region.

-- ---------------------------------------------------------------------
-- Q11. AFTER cleaning: reconcile the clean table with the raw table.
-- Clean rows must equal raw rows minus the rows removed in cleaning
-- (see data/processed/cleaning_log.csv).
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM sales_raw)  AS raw_rows,
    (SELECT COUNT(*) FROM fact_sales) AS clean_rows,
    (SELECT COUNT(*) FROM sales_raw) - (SELECT COUNT(*) FROM fact_sales) AS rows_removed;
