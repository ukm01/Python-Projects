SELECT COUNT(*) AS total_customers FROM customers;
SELECT COUNT(*) AS total_products FROM products;
SELECT COUNT(*) AS total_stores FROM stores;
SELECT COUNT(*) AS total_orders FROM orders;
SELECT COUNT(*) AS total_returns FROM returns;

SELECT * FROM customers LIMIT 5;

-- list all kpis 

SELECT 
    SUM(net_sales) AS total_revenue,
    SUM(profit) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(quantity) AS total_quantity_sold,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders;

-- revenue by channel
SELECT
    channel,
    SUM(net_sales) AS total_revenue,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(net_sales), 2) AS avg_order_value
FROM orders
GROUP BY channel
ORDER BY total_revenue DESC;

--revenue by category
SELECT
    p.category,
    SUM(o.net_sales) AS total_revenue,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND((SUM(o.profit) / SUM(o.net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

--Top 10 products by revenue
SELECT
    p.product_name,
    p.category,
    SUM(o.net_sales) AS total_revenue,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND((SUM(o.profit) / SUM(o.net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_name,
    p.category
ORDER BY total_revenue DESC
LIMIT 10;


--Monthly revenue trend

SELECT
    EXTRACT(YEAR FROM order_date) AS year,
    EXTRACT(MONTH FROM order_date) AS month,
    TO_CHAR(order_date, 'Month') AS month_name,
    SUM(net_sales) AS total_revenue,
    SUM(profit) AS total_profit,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(net_sales), 2) AS avg_order_value
FROM orders
GROUP BY
    EXTRACT(YEAR FROM order_date),
    EXTRACT(MONTH FROM order_date),
    TO_CHAR(order_date, 'Month')
ORDER BY
    year,
    month;

--Customer segment performance

SELECT
    c.segment,
    SUM(o.net_sales) AS total_revenue,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    ROUND(AVG(o.net_sales), 2) AS avg_order_value,
    ROUND((SUM(o.profit) / SUM(o.net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_revenue DESC;

--City-wise sales performance
SELECT
    c.city,
    c.state,
    SUM(o.net_sales) AS total_revenue,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    ROUND(AVG(o.net_sales), 2) AS avg_order_value
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.city,
    c.state
ORDER BY total_revenue DESC
LIMIT 20;

--Store-wise sales performance
SELECT
    s.store_id,
    s.store_name,
    s.city,
    s.state,
    SUM(o.net_sales) AS total_revenue,
    SUM(o.profit) AS total_profit,
    COUNT(o.order_id) AS total_orders,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND(AVG(o.net_sales), 2) AS avg_order_value,
    ROUND((SUM(o.profit) / SUM(o.net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders o
JOIN stores s
    ON o.store_id = s.store_id
GROUP BY
    s.store_id,
    s.store_name,
    s.city,
    s.state
ORDER BY total_revenue DESC
LIMIT 20;

--Return summary
SELECT
    COUNT(r.return_id) AS total_returns,
    COUNT(DISTINCT r.order_id) AS returned_orders,
    ROUND(
        COUNT(DISTINCT r.order_id) * 100.0 / COUNT(DISTINCT o.order_id),
        2
    ) AS return_rate_percentage,
    SUM(o.net_sales) AS returned_order_revenue
FROM returns r
JOIN orders o
    ON r.order_id = o.order_id;

--Returns by product category

SELECT
    p.category,
    COUNT(r.return_id) AS total_returns,
    COUNT(DISTINCT r.order_id) AS returned_orders,
    SUM(o.net_sales) AS returned_revenue,
    ROUND(
        COUNT(DISTINCT r.order_id) * 100.0 / COUNT(DISTINCT o.order_id),
        2
    ) AS category_return_rate_percentage
FROM orders o
JOIN products p
    ON o.product_id = p.product_id
LEFT JOIN returns r
    ON o.order_id = r.order_id
GROUP BY p.category
ORDER BY category_return_rate_percentage DESC;

--Discount impact analysis
SELECT
    CASE
        WHEN discount_pct > 0 THEN 'Discount Applied'
        ELSE 'No Discount'
    END AS discount_status,
    SUM(net_sales) AS total_revenue,
    SUM(profit) AS total_profit,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(net_sales), 2) AS avg_order_value,
    ROUND((SUM(profit) / SUM(net_sales)) * 100, 2) AS profit_margin_percentage
FROM orders
GROUP BY
    CASE
        WHEN discount_pct > 0 THEN 'Discount Applied'
        ELSE 'No Discount'
    END
ORDER BY total_revenue DESC;

--Payment method analysis

SELECT
    payment_mode,
    SUM(net_sales) AS total_revenue,
    COUNT(order_id) AS total_orders,
    ROUND(AVG(net_sales), 2) AS avg_order_value,
    ROUND(
        COUNT(order_id) * 100.0 / SUM(COUNT(order_id)) OVER (),
        2
    ) AS order_percentage
FROM orders
GROUP BY payment_mode
ORDER BY total_revenue DESC;

--Repeat customer analysis

SELECT
    customer_type,
    COUNT(customer_id) AS total_customers
FROM (
    SELECT
        customer_id,
        CASE
            WHEN COUNT(order_id) > 1 THEN 'Repeat Customer'
            ELSE 'One-time Customer'
        END AS customer_type
    FROM orders
    GROUP BY customer_id
) customer_orders
GROUP BY customer_type;







