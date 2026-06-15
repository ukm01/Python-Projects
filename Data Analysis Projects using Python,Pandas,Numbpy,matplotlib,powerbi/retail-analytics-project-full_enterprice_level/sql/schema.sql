
-- Retail Analytics Project SQL Schema
-- Recommended database: PostgreSQL or SQL Server.
-- If using SQL Server, change DATE syntax only if needed.

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    gender VARCHAR(20),
    age INT,
    city VARCHAR(50),
    segment VARCHAR(30),
    signup_date DATE,
    state VARCHAR(50)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(150),
    category VARCHAR(50),
    brand VARCHAR(50),
    list_price DECIMAL(12,2),
    cost_price DECIMAL(12,2)
);

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    store_type VARCHAR(50)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    order_date DATE,
    customer_id INT,
    product_id INT,
    store_id INT,
    channel VARCHAR(30),
    payment_mode VARCHAR(30),
    quantity INT,
    discount_pct DECIMAL(5,2),
    unit_price DECIMAL(12,2),
    gross_sales DECIMAL(12,2),
    discount_amount DECIMAL(12,2),
    net_sales DECIMAL(12,2),
    cost_amount DECIMAL(12,2),
    profit DECIMAL(12,2)
);

CREATE TABLE returns (
    return_id INT PRIMARY KEY,
    order_id INT,
    return_date DATE,
    return_reason VARCHAR(50),
    refund_amount DECIMAL(12,2)
);
