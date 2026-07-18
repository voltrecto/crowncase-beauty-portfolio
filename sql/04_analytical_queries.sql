-- 8 business queries against orders_clean

USE CrownCaseBeauty_Portfolio;
GO

-- 1. monthly revenue by channel
SELECT
    channel,
    YEAR(order_date) AS order_year,
    MONTH(order_date) AS order_month,
    SUM(unit_price * units_sold) AS revenue
FROM orders_clean
GROUP BY channel, YEAR(order_date), MONTH(order_date)
ORDER BY channel, order_year, order_month;

-- 2. gross margin by category
SELECT
    p.category,
    SUM(oc.unit_price * oc.units_sold) AS revenue,
    SUM(p.cost_of_goods * oc.units_sold) AS total_cost,
    ROUND(
        (SUM(oc.unit_price * oc.units_sold) - SUM(p.cost_of_goods * oc.units_sold))
        / SUM(oc.unit_price * oc.units_sold) * 100
    , 2) AS gross_margin_pct
FROM orders_clean oc
JOIN products p ON oc.sku = p.sku
GROUP BY p.category
ORDER BY gross_margin_pct DESC;

-- 3. return rate by channel
SELECT
    channel,
    COUNT(*) AS total_orders,
    SUM(CAST(return_flag AS INT)) AS returned_orders,
    ROUND(AVG(CAST(return_flag AS FLOAT)) * 100, 2) AS return_rate_pct
FROM orders_clean
GROUP BY channel
ORDER BY channel;

-- 4. same-sku website vs amazon fbm profitability comparison
WITH channel_stats AS (
    SELECT
        oc.sku,
        oc.channel,
        SUM(oc.unit_price * oc.units_sold) AS revenue,
        SUM(p.cost_of_goods * oc.units_sold) AS total_cost,
        SUM(oc.platform_fee) AS total_platform_fee
    FROM orders_clean oc
    JOIN products p ON oc.sku = p.sku
    GROUP BY oc.sku, oc.channel
)
SELECT
    w.sku,
    p.category,
    w.revenue AS website_revenue,
    f.revenue AS fbm_revenue,
    ROUND((w.revenue - w.total_cost - w.total_platform_fee) / w.revenue * 100, 2) AS website_margin_pct,
    ROUND((f.revenue - f.total_cost - f.total_platform_fee) / f.revenue * 100, 2) AS fbm_margin_pct
FROM channel_stats w
JOIN channel_stats f ON w.sku = f.sku AND w.channel = 'Website' AND f.channel = 'Amazon FBM'
JOIN products p ON w.sku = p.sku
ORDER BY p.category, w.sku;

-- 5. top 10 skus by revenue
SELECT TOP 10
    oc.sku,
    p.product_name,
    p.category,
    SUM(oc.unit_price * oc.units_sold) AS revenue
FROM orders_clean oc
JOIN products p ON oc.sku = p.sku
GROUP BY oc.sku, p.product_name, p.category
ORDER BY revenue DESC;

-- 6. month-over-month revenue growth
WITH monthly_revenue AS (
    SELECT
        YEAR(order_date) AS order_year,
        MONTH(order_date) AS order_month,
        SUM(unit_price * units_sold) AS revenue
    FROM orders_clean
    GROUP BY YEAR(order_date), MONTH(order_date)
)
SELECT
    order_year,
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_year, order_month) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY order_year, order_month))
        / LAG(revenue) OVER (ORDER BY order_year, order_month) * 100
    , 2) AS mom_growth_pct
FROM monthly_revenue
ORDER BY order_year, order_month;

-- 7. running total of units sold by channel
SELECT
    channel,
    YEAR(order_date) AS order_year,
    MONTH(order_date) AS order_month,
    SUM(units_sold) AS monthly_units,
    SUM(SUM(units_sold)) OVER (PARTITION BY channel ORDER BY YEAR(order_date), MONTH(order_date)) AS running_total_units
FROM orders_clean
GROUP BY channel, YEAR(order_date), MONTH(order_date)
ORDER BY channel, order_year, order_month;

-- 8. average order value by channel
SELECT
    channel,
    COUNT(*) AS total_orders,
    ROUND(AVG(unit_price * units_sold), 2) AS avg_order_value
FROM orders_clean
GROUP BY channel
ORDER BY channel;
