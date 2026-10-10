-- OLAP query examples for Oracle. Run after schema and ETL are complete.

-- 1. ROLL-UP: summarize sales by year and category.
SELECT d.year_number, p.category_name, SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_product p ON p.product_key = f.product_key
GROUP BY ROLLUP (d.year_number, p.category_name)
ORDER BY d.year_number, p.category_name;

-- 2. DRILL-DOWN: year -> month -> day totals.
SELECT d.year_number, d.month_number, d.full_date, SUM(f.sales_amount) AS total_sales
FROM fact_sales f JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year_number, d.month_number, d.full_date
ORDER BY d.year_number, d.month_number, d.full_date;

-- 3. SLICE: sales for one region.
SELECT r.region_name, SUM(f.sales_amount) AS total_sales
FROM fact_sales f JOIN dim_region r ON r.region_key = f.region_key
WHERE r.region_name = 'South'
GROUP BY r.region_name;

-- 4. DICE: filter on multiple dimensions.
SELECT r.region_name, p.category_name, s.segment_name, SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_region r ON r.region_key = f.region_key
JOIN dim_product p ON p.product_key = f.product_key
JOIN dim_customer_segment s ON s.segment_key = f.segment_key
WHERE r.region_name IN ('North', 'West')
  AND p.category_name IN ('Electronics', 'Home')
  AND s.segment_name = 'Consumer'
GROUP BY r.region_name, p.category_name, s.segment_name
ORDER BY total_sales DESC;

-- 5. PIVOT: category sales across regions.
SELECT *
FROM (
  SELECT p.category_name, r.region_name, f.sales_amount
  FROM fact_sales f
  JOIN dim_product p ON p.product_key = f.product_key
  JOIN dim_region r ON r.region_key = f.region_key
)
PIVOT (SUM(sales_amount) FOR region_name IN
  ('North' AS NORTH, 'South' AS SOUTH, 'East' AS EAST, 'West' AS WEST, 'Central' AS CENTRAL))
ORDER BY category_name;
