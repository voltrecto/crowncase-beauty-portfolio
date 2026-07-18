-- loads the 3 csvs, products/channels first since orders has an FK on products(sku)
-- copied csv to C:\SQLData since the SQL service account can't read the project folder
-- using \n instead of \r\n for ROWTERMINATOR, \r\n was silently loading 0 rows

USE CrownCaseBeauty_Portfolio;
GO

BULK INSERT products
FROM 'C:\SQLData\products.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', TABLOCK);

BULK INSERT channels
FROM 'C:\SQLData\channels.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', TABLOCK);

BULK INSERT orders
FROM 'C:\SQLData\orders.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', TABLOCK);
GO

SELECT COUNT(*) AS product_count FROM products;   -- expected 170
SELECT COUNT(*) AS channel_count FROM channels;   -- expected 2
SELECT COUNT(*) AS order_count FROM orders;        -- expected 10015
