/*
============================================
Projeto: Pipeline ETL de E-commerce
Autor: Murilo Henrique Nellis

Objetivo:
Consultas SQL utilizadas para responder
às perguntas de negócio após o carregamento
dos dados no PostgreSQL.
============================================
*/

-- 1. Faturamento total
SELECT
    ROUND(SUM("Revenue")::numeric, 2) AS total_revenue
FROM fato_vendas;

-- 2. Top 10 produtos mais vendidos
SELECT
    p."Description",
    SUM(v."Quantity") AS quantity_sold
FROM dim_produtos p
JOIN fato_vendas v ON p."StockCode" = v."StockCode"
GROUP BY p."Description"
ORDER BY quantity_sold DESC
LIMIT 10;

-- 3. Top 10 clientes por faturamento
SELECT
    "CustomerID",
    ROUND(SUM("Revenue")::numeric, 2) AS customer_revenue
FROM fato_vendas
GROUP BY "CustomerID"
ORDER BY customer_revenue DESC
LIMIT 10;

-- 4. Faturamento por país
SELECT
    c."Country",
    ROUND(SUM(v."Revenue")::numeric, 2) AS country_revenue
FROM dim_clientes c
JOIN fato_vendas v ON c."CustomerID" = v."CustomerID"
GROUP BY c."Country"
ORDER BY country_revenue DESC;

-- 5. Faturamento por mês
SELECT
    "mes",
    ROUND(SUM("Revenue")::numeric, 2) AS month_revenue
FROM fato_vendas
GROUP BY "mes"
ORDER BY "mes";

-- 6. Quantidade de pedidos por mês
SELECT
    "mes",
    COUNT(DISTINCT "InvoiceNo") AS total_orders
FROM fato_vendas
GROUP BY "mes"
ORDER BY "mes";

-- 7. Ticket médio por pedido
SELECT
    ROUND(
        SUM("Revenue")::numeric /
        COUNT(DISTINCT "InvoiceNo"),
        2
    ) AS average_ticket
FROM fato_vendas;

-- 8. Valor médio por item vendido
SELECT
    ROUND(
        SUM("Revenue")::numeric /
        SUM("Quantity"),
        2
    ) AS average_item_value
FROM fato_vendas;

-- 9. Quantidade de clientes únicos
SELECT
    COUNT(DISTINCT "CustomerID") AS unique_customers
FROM fato_vendas;

-- 10. Quantidade total de produtos vendidos
SELECT
    SUM("Quantity") AS products_sold
FROM fato_vendas;