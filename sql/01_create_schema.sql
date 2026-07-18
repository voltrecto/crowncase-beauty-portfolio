-- creates the CrownCaseBeauty_Portfolio database and its 3 tables

CREATE DATABASE CrownCaseBeauty_Portfolio;
GO

USE CrownCaseBeauty_Portfolio;
GO

CREATE TABLE products (
    sku VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(30) NOT NULL,
    color VARCHAR(30) NOT NULL,
    cost_of_goods DECIMAL(10,2) NOT NULL
);

CREATE TABLE channels (
    channel VARCHAR(20) PRIMARY KEY,
    avg_fee_pct DECIMAL(5,4) NOT NULL,
    avg_shipping_cost DECIMAL(10,2) NOT NULL
);

-- no primary key on orders, duplicate order_ids in orders.csv would break a PK/unique constraint
-- tried an identity surrogate key first but BULK INSERT maps columns by position and broke on it

CREATE TABLE orders (
    order_id VARCHAR(20) NOT NULL,
    order_date VARCHAR(20) NOT NULL,
    sku VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    units_sold INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) NULL,
    shipping_cost DECIMAL(10,2) NULL,
    platform_fee DECIMAL(10,2) NOT NULL,
    return_flag VARCHAR(10) NOT NULL,
    CONSTRAINT FK_orders_products_sku FOREIGN KEY (sku) REFERENCES products(sku)
);
GO
