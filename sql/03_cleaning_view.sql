-- cleans orders: corrects date formats, normalizes channel casing, fills nulls, dedupes, converts return_flag to 0 or 1
-- reads from raw orders, phase 3 python does its own independent clean from the same raw table

USE CrownCaseBeauty_Portfolio;
GO

CREATE VIEW orders_clean AS
WITH deduped AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY (SELECT NULL)) AS rn
    FROM orders
)
SELECT
    order_id,
    CASE
        WHEN order_date LIKE '____-__-__' THEN TRY_CONVERT(DATE, order_date, 23)
        WHEN order_date LIKE '__/__/____' THEN TRY_CONVERT(DATE, order_date, 101)
    END AS order_date,
    sku,
    CASE
        WHEN UPPER(channel) = 'WEBSITE' THEN 'Website'
        WHEN UPPER(channel) = 'AMAZON FBM' THEN 'Amazon FBM'
        ELSE channel
    END AS channel,
    units_sold,
    unit_price,
    COALESCE(discount_amount, 0) AS discount_amount,
    COALESCE(shipping_cost, 6.50) AS shipping_cost,
    platform_fee,
    CASE
        WHEN return_flag = 'True' THEN CAST(1 AS BIT)
        WHEN return_flag = 'False' THEN CAST(0 AS BIT)
    END AS return_flag
FROM deduped
WHERE rn = 1;
GO
