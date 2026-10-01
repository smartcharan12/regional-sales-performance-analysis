-- =====================================================================
-- schema.sql  -  Database, tables and data load (MySQL 8)
-- =====================================================================
-- WHAT THIS FILE DOES
--   1. Creates a database called retailco.
--   2. Creates a raw staging table (sales_raw) that accepts the messy
--      export exactly as it is - every column is text.
--   3. Creates a STAR SCHEMA (1 fact table + 4 dimension tables) for the
--      cleaned data produced by Python (data/processed/powerbi/*.csv).
--   4. Loads the CSV files.
--   5. Creates a convenience view (v_sales) that joins everything back
--      into one wide table for simple analysis queries.
--
-- HOW TO RUN (from the project root folder)
--   mysql --local-infile=1 -u root -p < sql/schema.sql
--   (LOCAL INFILE must also be enabled on the server:
--    SET GLOBAL local_infile = 1;)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS retailco;
USE retailco;

DROP VIEW  IF EXISTS v_sales;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_geography;
DROP TABLE IF EXISTS sales_raw;

-- ---------------------------------------------------------------------
-- 1. RAW STAGING TABLE
-- Everything is VARCHAR on purpose: raw data contains values like
-- "$1,234.50" or "2023-02-30" that would be rejected by numeric/date
-- columns. We load first, then inspect with data_quality.sql.
-- ---------------------------------------------------------------------
CREATE TABLE sales_raw (
    order_id       VARCHAR(30),
    order_date     VARCHAR(30),
    ship_date      VARCHAR(30),
    ship_mode      VARCHAR(30),
    customer_id    VARCHAR(20),
    customer_name  VARCHAR(100),
    segment        VARCHAR(30),
    country        VARCHAR(50),
    city           VARCHAR(60),
    state          VARCHAR(60),
    region         VARCHAR(30),
    product_id     VARCHAR(20),
    category       VARCHAR(30),
    sub_category   VARCHAR(30),
    product_name   VARCHAR(150),
    sales          VARCHAR(30),
    quantity       VARCHAR(10),
    discount       VARCHAR(10),
    profit         VARCHAR(30)
);

-- ---------------------------------------------------------------------
-- 2. DIMENSION TABLES  (the "who / what / where / when")
-- Each has a PRIMARY KEY: a column whose value is unique for every row.
-- ---------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key      INT          PRIMARY KEY,     -- 20240131
    full_date     DATE         NOT NULL UNIQUE,
    year          SMALLINT     NOT NULL,
    quarter       CHAR(2)      NOT NULL,        -- Q1..Q4
    month_number  TINYINT      NOT NULL,
    month_name    CHAR(3)      NOT NULL,        -- Jan..Dec
    yyyy_mm    CHAR(7)      NOT NULL,        -- 2024-01
    weekday       CHAR(3)      NOT NULL,
    is_weekend    BOOLEAN      NOT NULL
);

CREATE TABLE dim_customer (
    customer_id    VARCHAR(20)  PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    segment        VARCHAR(30)  NOT NULL
);

CREATE TABLE dim_product (
    product_id     VARCHAR(20)  PRIMARY KEY,
    product_name   VARCHAR(150) NOT NULL,
    category       VARCHAR(30)  NOT NULL,
    sub_category   VARCHAR(30)  NOT NULL
);

CREATE TABLE dim_geography (
    geo_key   INT          PRIMARY KEY,   -- surrogate key (no natural ID exists)
    country   VARCHAR(50)  NOT NULL,
    region    VARCHAR(30)  NOT NULL,
    state     VARCHAR(60)  NOT NULL,
    city      VARCHAR(60)  NOT NULL,
    UNIQUE (state, city)
);

-- ---------------------------------------------------------------------
-- 3. FACT TABLE  (one row per order line = the "grain")
-- FOREIGN KEYS point to the dimension tables and guarantee that every
-- sale refers to a customer/product/date/place that actually exists.
-- ---------------------------------------------------------------------
CREATE TABLE fact_sales (
    sales_key        INT            PRIMARY KEY,
    order_id         VARCHAR(30)    NOT NULL,
    order_date_key   INT            NOT NULL,
    order_date       DATE           NOT NULL,
    ship_date        DATE           NULL,        -- NULL when the source date was impossible
    ship_mode        VARCHAR(30)    NOT NULL,
    customer_id      VARCHAR(20)    NOT NULL,
    product_id       VARCHAR(20)    NOT NULL,
    geo_key          INT            NOT NULL,
    sales            DECIMAL(12,2)  NOT NULL,
    quantity         INT            NOT NULL,
    discount         DECIMAL(4,2)   NOT NULL,
    profit           DECIMAL(12,2)  NOT NULL,
    gross_sales      DECIMAL(12,2)  NOT NULL,
    discount_amount  DECIMAL(12,2)  NOT NULL,
    shipping_days    INT            NULL,
    CONSTRAINT fk_sales_date     FOREIGN KEY (order_date_key) REFERENCES dim_date (date_key),
    CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id)    REFERENCES dim_customer (customer_id),
    CONSTRAINT fk_sales_product  FOREIGN KEY (product_id)     REFERENCES dim_product (product_id),
    CONSTRAINT fk_sales_geo      FOREIGN KEY (geo_key)        REFERENCES dim_geography (geo_key),
    CONSTRAINT chk_sales_positive CHECK (sales > 0),
    CONSTRAINT chk_quantity       CHECK (quantity > 0),
    CONSTRAINT chk_discount       CHECK (discount BETWEEN 0 AND 1)
);

-- Indexes on the columns we filter and join on most often
CREATE INDEX ix_fact_order_date ON fact_sales (order_date);
CREATE INDEX ix_fact_order_id   ON fact_sales (order_id);

-- ---------------------------------------------------------------------
-- 4. LOAD THE CSV FILES
-- IGNORE 1 LINES skips the header row. Empty strings are converted to
-- NULL with NULLIF so that blank ship dates load correctly.
-- ---------------------------------------------------------------------
LOAD DATA LOCAL INFILE 'data/raw/sales_raw.csv'
INTO TABLE sales_raw
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'data/processed/powerbi/DimDate.csv'
INTO TABLE dim_date
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(date_key, full_date, year, quarter, month_number, month_name, yyyy_mm, weekday, @is_weekend)
SET is_weekend = (@is_weekend = 'True');

LOAD DATA LOCAL INFILE 'data/processed/powerbi/DimCustomer.csv'
INTO TABLE dim_customer
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'data/processed/powerbi/DimProduct.csv'
INTO TABLE dim_product
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'data/processed/powerbi/DimGeography.csv'
INTO TABLE dim_geography
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'data/processed/powerbi/FactSales.csv'
INTO TABLE fact_sales
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(sales_key, order_id, order_date_key, order_date, @ship_date, ship_mode,
 customer_id, product_id, geo_key, sales, quantity, discount, profit,
 gross_sales, discount_amount, @shipping_days)
SET ship_date     = NULLIF(@ship_date, ''),
    shipping_days = NULLIF(@shipping_days, '');

-- ---------------------------------------------------------------------
-- 5. CONVENIENCE VIEW
-- A view is a saved query. v_sales re-joins the star schema into one
-- wide table so beginner queries do not need to repeat the joins.
-- ---------------------------------------------------------------------
CREATE VIEW v_sales AS
SELECT
    f.sales_key,
    f.order_id,
    f.order_date,
    d.year,
    d.quarter,
    d.month_number,
    d.yyyy_mm,
    f.ship_mode,
    f.shipping_days,
    c.customer_id,
    c.customer_name,
    c.segment,
    g.region,
    g.state,
    g.city,
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    f.sales,
    f.quantity,
    f.discount,
    f.profit,
    f.gross_sales,
    f.discount_amount
FROM fact_sales    AS f
JOIN dim_date      AS d ON d.date_key    = f.order_date_key
JOIN dim_customer  AS c ON c.customer_id = f.customer_id
JOIN dim_product   AS p ON p.product_id  = f.product_id
JOIN dim_geography AS g ON g.geo_key     = f.geo_key;

-- Quick check: row counts should match the Python pipeline output
SELECT 'sales_raw' AS table_name, COUNT(*) AS row_count FROM sales_raw
UNION ALL SELECT 'fact_sales',    COUNT(*) FROM fact_sales
UNION ALL SELECT 'dim_date',      COUNT(*) FROM dim_date
UNION ALL SELECT 'dim_customer',  COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_product',   COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_geography', COUNT(*) FROM dim_geography;
