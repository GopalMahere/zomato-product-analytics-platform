-- ==============================================================================
-- Zomato Product Analytics Platform — Analytical Queries
-- Target DBMS : SQL Server 2022
-- Database    : Zomato_Product_Analytics
-- Description : 25 analytical queries covering all major business domains
-- ==============================================================================

USE Zomato_Product_Analytics;
GO

-- ==============================================================================
-- SECTION 1: EXECUTIVE KPIs
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 1: Full Executive KPI Dashboard (Delivered Orders Only)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    COUNT(DISTINCT order_id)                                     AS Total_Orders,
    COUNT(DISTINCT customer_id)                                  AS Total_Customers,
    COUNT(DISTINCT restaurant_id)                                AS Total_Restaurants,
    ROUND(SUM(final_amount), 2)                                  AS Total_Revenue,
    ROUND(AVG(final_amount), 2)                                  AS Avg_Order_Value,
    ROUND(AVG(CAST(delivery_time_minutes AS FLOAT)), 1)          AS Avg_Delivery_Time_Min,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                            AS Cancellation_Rate_Pct,
    ROUND(
        100.0 * SUM(CASE WHEN delivery_time_minutes > 30 THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                            AS SLA_Breach_Rate_Pct
FROM dbo.Orders;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 2: Monthly Revenue Trend
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    YEAR(order_date)                                             AS Year,
    MONTH(order_date)                                            AS Month,
    FORMAT(order_date, 'MMM yyyy')                               AS Month_Label,
    COUNT(order_id)                                              AS Total_Orders,
    SUM(CASE WHEN status = 'Delivered' THEN final_amount ELSE 0 END) AS Revenue,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END)        AS Cancelled_Orders,
    ROUND(AVG(final_amount), 2)                                  AS Avg_Order_Value
FROM dbo.Orders
GROUP BY YEAR(order_date), MONTH(order_date), FORMAT(order_date, 'MMM yyyy')
ORDER BY Year, Month;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 3: Month-Over-Month Revenue Growth
-- ─────────────────────────────────────────────────────────────────────────────
WITH Monthly_Revenue AS (
    SELECT
        YEAR(order_date)  AS Year,
        MONTH(order_date) AS Month,
        FORMAT(order_date, 'MMM yyyy') AS Month_Label,
        SUM(CASE WHEN status = 'Delivered' THEN final_amount ELSE 0 END) AS Revenue
    FROM dbo.Orders
    GROUP BY YEAR(order_date), MONTH(order_date), FORMAT(order_date, 'MMM yyyy')
)
SELECT
    Year, Month, Month_Label, Revenue,
    LAG(Revenue) OVER (ORDER BY Year, Month)                    AS Prev_Month_Revenue,
    ROUND(
        100.0 * (Revenue - LAG(Revenue) OVER (ORDER BY Year, Month))
        / NULLIF(LAG(Revenue) OVER (ORDER BY Year, Month), 0), 2
    )                                                            AS MoM_Growth_Pct
FROM Monthly_Revenue
ORDER BY Year, Month;
GO

-- ==============================================================================
-- SECTION 2: CUSTOMER ANALYTICS
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 4: Top 10 Customers by Total Spend
-- ─────────────────────────────────────────────────────────────────────────────
SELECT TOP 10
    c.customer_id,
    c.customer_name,
    c.city,
    c.zomato_gold,
    COUNT(o.order_id)                                            AS Total_Orders,
    ROUND(SUM(o.final_amount), 2)                                AS Total_Spent,
    ROUND(AVG(o.final_amount), 2)                                AS Avg_Order_Value
FROM dbo.Customers c
JOIN dbo.Orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.customer_name, c.city, c.zomato_gold
ORDER BY Total_Spent DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 5: Gold vs Non-Gold Member Performance
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    CASE WHEN c.zomato_gold = 1 THEN 'Gold Member' ELSE 'Regular Member' END AS Member_Type,
    COUNT(DISTINCT c.customer_id)                                AS Customer_Count,
    COUNT(o.order_id)                                            AS Total_Orders,
    ROUND(SUM(o.final_amount), 2)                                AS Total_Revenue,
    ROUND(AVG(o.final_amount), 2)                                AS Avg_Order_Value,
    ROUND(AVG(o.discount), 2)                                    AS Avg_Discount
FROM dbo.Customers c
JOIN dbo.Orders o ON c.customer_id = o.customer_id
WHERE o.status = 'Delivered'
GROUP BY CASE WHEN c.zomato_gold = 1 THEN 'Gold Member' ELSE 'Regular Member' END;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 6: Customer Cohort — First-Order Month Retention
-- ─────────────────────────────────────────────────────────────────────────────
WITH First_Order AS (
    SELECT
        customer_id,
        MIN(order_date)                                          AS First_Order_Date,
        EOMONTH(MIN(order_date))                                 AS Cohort_Month
    FROM dbo.Orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
),
Customer_Activity AS (
    SELECT
        o.customer_id,
        fo.Cohort_Month,
        DATEDIFF(MONTH, fo.Cohort_Month, o.order_date)          AS Month_Number
    FROM dbo.Orders o
    JOIN First_Order fo ON o.customer_id = fo.customer_id
    WHERE o.status = 'Delivered'
)
SELECT
    FORMAT(Cohort_Month, 'MMM yyyy')                             AS Cohort,
    Month_Number,
    COUNT(DISTINCT customer_id)                                  AS Active_Customers
FROM Customer_Activity
WHERE Month_Number BETWEEN 0 AND 6
GROUP BY Cohort_Month, Month_Number
ORDER BY Cohort_Month, Month_Number;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 7: Customer Lifetime Value (CLV) Segments
-- ─────────────────────────────────────────────────────────────────────────────
WITH Customer_Spend AS (
    SELECT
        customer_id,
        ROUND(SUM(final_amount), 2)                              AS Total_Spend,
        COUNT(order_id)                                          AS Total_Orders
    FROM dbo.Orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN Total_Spend >= 15000 THEN 'High Value (₹15K+)'
        WHEN Total_Spend >= 8000  THEN 'Mid Value (₹8K–15K)'
        WHEN Total_Spend >= 3000  THEN 'Low Value (₹3K–8K)'
        ELSE 'At Risk (<₹3K)'
    END                                                          AS CLV_Segment,
    COUNT(customer_id)                                           AS Customer_Count,
    ROUND(AVG(Total_Spend), 2)                                   AS Avg_Spend,
    ROUND(AVG(CAST(Total_Orders AS FLOAT)), 1)                   AS Avg_Orders
FROM Customer_Spend
GROUP BY
    CASE
        WHEN Total_Spend >= 15000 THEN 'High Value (₹15K+)'
        WHEN Total_Spend >= 8000  THEN 'Mid Value (₹8K–15K)'
        WHEN Total_Spend >= 3000  THEN 'Low Value (₹3K–8K)'
        ELSE 'At Risk (<₹3K)'
    END
ORDER BY Avg_Spend DESC;
GO

-- ==============================================================================
-- SECTION 3: RESTAURANT ANALYTICS
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 8: Top 10 Restaurants by Revenue
-- ─────────────────────────────────────────────────────────────────────────────
SELECT TOP 10
    r.restaurant_id,
    r.restaurant_name,
    r.city,
    r.cuisine,
    COUNT(o.order_id)                                            AS Total_Orders,
    ROUND(SUM(o.final_amount), 2)                                AS Revenue,
    ROUND(AVG(o.final_amount), 2)                                AS Avg_Order_Value,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)), 1)        AS Avg_Delivery_Time
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'Delivered'
GROUP BY r.restaurant_id, r.restaurant_name, r.city, r.cuisine
ORDER BY Revenue DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 9: Revenue by City
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.city,
    COUNT(DISTINCT r.restaurant_id)                              AS Total_Restaurants,
    COUNT(o.order_id)                                            AS Total_Orders,
    ROUND(SUM(o.final_amount), 2)                                AS Total_Revenue,
    ROUND(AVG(o.final_amount), 2)                                AS Avg_Order_Value,
    ROUND(
        100.0 * SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2
    )                                                            AS Cancellation_Rate_Pct
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.city
ORDER BY Total_Revenue DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 10: Cuisine Popularity and Performance
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.cuisine,
    COUNT(o.order_id)                                            AS Total_Orders,
    ROUND(SUM(CASE WHEN o.status='Delivered' THEN o.final_amount ELSE 0 END), 2) AS Revenue,
    ROUND(AVG(o.final_amount), 2)                                AS Avg_Order_Value,
    ROUND(
        100.0 * SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2
    )                                                            AS Cancellation_Rate_Pct,
    ROUND(AVG(r.average_rating), 2)                              AS Avg_Restaurant_Rating
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.cuisine
ORDER BY Total_Orders DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 11: Restaurant Ratings with Review Sentiment Count
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.restaurant_name,
    r.city,
    r.cuisine,
    ROUND(AVG(CAST(rv.rating AS FLOAT)), 2)                      AS Avg_Review_Rating,
    COUNT(rv.review_id)                                          AS Total_Reviews,
    SUM(CASE WHEN rv.rating >= 4 THEN 1 ELSE 0 END)              AS Positive_Reviews,
    SUM(CASE WHEN rv.rating <= 2 THEN 1 ELSE 0 END)              AS Negative_Reviews,
    ROUND(100.0 * SUM(CASE WHEN rv.rating >= 4 THEN 1 ELSE 0 END) / COUNT(rv.review_id), 1)
                                                                 AS Positive_Pct
FROM dbo.Reviews rv
JOIN dbo.Restaurants r ON rv.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_name, r.city, r.cuisine
HAVING COUNT(rv.review_id) >= 5
ORDER BY Avg_Review_Rating DESC;
GO

-- ==============================================================================
-- SECTION 4: DELIVERY & OPERATIONS
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 12: Top 10 Delivery Partners by Deliveries
-- ─────────────────────────────────────────────────────────────────────────────
SELECT TOP 10
    d.partner_id,
    d.partner_name,
    d.city,
    d.vehicle_type,
    d.rating                                                     AS Partner_Rating,
    COUNT(o.order_id)                                            AS Total_Deliveries,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)), 1)        AS Avg_Delivery_Time,
    MIN(o.delivery_time_minutes)                                 AS Best_Delivery_Time,
    MAX(o.delivery_time_minutes)                                 AS Worst_Delivery_Time
FROM dbo.Orders o
JOIN dbo.Delivery_Partners d ON o.partner_id = d.partner_id
WHERE o.status = 'Delivered'
GROUP BY d.partner_id, d.partner_name, d.city, d.vehicle_type, d.rating
ORDER BY Total_Deliveries DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 13: Delivery Performance by Vehicle Type
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    d.vehicle_type,
    COUNT(o.order_id)                                            AS Total_Deliveries,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)), 1)        AS Avg_Delivery_Time,
    ROUND(
        100.0 * SUM(CASE WHEN o.delivery_time_minutes > 30 THEN 1 ELSE 0 END)
        / COUNT(o.order_id), 2
    )                                                            AS SLA_Breach_Rate_Pct
FROM dbo.Orders o
JOIN dbo.Delivery_Partners d ON o.partner_id = d.partner_id
WHERE o.status = 'Delivered'
GROUP BY d.vehicle_type
ORDER BY Avg_Delivery_Time;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 14: Peak Ordering Hours Analysis
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    DATEPART(HOUR, order_time)                                   AS Hour_of_Day,
    COUNT(order_id)                                              AS Total_Orders,
    ROUND(SUM(CASE WHEN status='Delivered' THEN final_amount ELSE 0 END), 2) AS Revenue,
    ROUND(AVG(CAST(delivery_time_minutes AS FLOAT)), 1)          AS Avg_Delivery_Time
FROM dbo.Orders
GROUP BY DATEPART(HOUR, order_time)
ORDER BY Hour_of_Day;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 15: Cancellation Root Cause by City & Cuisine
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.city,
    r.cuisine,
    COUNT(o.order_id)                                            AS Total_Orders,
    SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END)      AS Cancelled_Orders,
    ROUND(
        100.0 * SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2
    )                                                            AS Cancellation_Rate_Pct
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.city, r.cuisine
HAVING COUNT(o.order_id) >= 20
ORDER BY Cancellation_Rate_Pct DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 16: SLA Breach Analysis (Deliveries > 30 Minutes)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.city,
    COUNT(o.order_id)                                            AS Total_Delivered,
    SUM(CASE WHEN o.delivery_time_minutes > 30 THEN 1 ELSE 0 END) AS SLA_Breached,
    ROUND(
        100.0 * SUM(CASE WHEN o.delivery_time_minutes > 30 THEN 1 ELSE 0 END) / COUNT(o.order_id), 2
    )                                                            AS SLA_Breach_Pct,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)), 1)        AS Avg_Delivery_Min
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'Delivered'
GROUP BY r.city
ORDER BY SLA_Breach_Pct DESC;
GO

-- ==============================================================================
-- SECTION 5: PAYMENT ANALYTICS
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 17: Payment Method Usage & Revenue
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    p.payment_method,
    COUNT(p.payment_id)                                          AS Total_Transactions,
    SUM(CASE WHEN p.payment_status = 'Success' THEN 1 ELSE 0 END) AS Successful,
    SUM(CASE WHEN p.payment_status = 'Failed'  THEN 1 ELSE 0 END) AS Failed,
    SUM(CASE WHEN p.payment_status = 'Refunded' THEN 1 ELSE 0 END) AS Refunded,
    ROUND(
        100.0 * SUM(CASE WHEN p.payment_status = 'Failed' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                            AS Failure_Rate_Pct
FROM dbo.Payments p
GROUP BY p.payment_method
ORDER BY Total_Transactions DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 18: Payment Failure Analysis (Linked to Orders)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    p.payment_status,
    o.status                                                     AS Order_Status,
    COUNT(*)                                                     AS Count,
    ROUND(SUM(o.final_amount), 2)                                AS Affected_Revenue
FROM dbo.Payments p
JOIN dbo.Orders o ON p.order_id = o.order_id
GROUP BY p.payment_status, o.status
ORDER BY p.payment_status, Count DESC;
GO

-- ==============================================================================
-- SECTION 6: DISCOUNT & REVENUE OPTIMIZATION
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 19: Discount Impact on Revenue
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN discount = 0              THEN 'No Discount'
        WHEN discount BETWEEN 1 AND 99 THEN 'Low Discount (₹1–99)'
        WHEN discount BETWEEN 100 AND 299 THEN 'Mid Discount (₹100–299)'
        ELSE 'High Discount (₹300+)'
    END                                                          AS Discount_Tier,
    COUNT(order_id)                                              AS Orders,
    ROUND(AVG(final_amount), 2)                                  AS Avg_Revenue_Per_Order,
    ROUND(SUM(discount), 2)                                      AS Total_Discount_Given,
    ROUND(SUM(final_amount), 2)                                  AS Total_Revenue
FROM dbo.Orders
WHERE status = 'Delivered'
GROUP BY
    CASE
        WHEN discount = 0              THEN 'No Discount'
        WHEN discount BETWEEN 1 AND 99 THEN 'Low Discount (₹1–99)'
        WHEN discount BETWEEN 100 AND 299 THEN 'Mid Discount (₹100–299)'
        ELSE 'High Discount (₹300+)'
    END
ORDER BY Total_Revenue DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 20: Revenue Leakage from Cancellations
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.city,
    SUM(CASE WHEN o.status = 'Cancelled' THEN o.order_amount ELSE 0 END) AS Revenue_Lost,
    COUNT(CASE WHEN o.status = 'Cancelled' THEN 1 END)           AS Cancelled_Orders,
    ROUND(
        100.0 * SUM(CASE WHEN o.status='Cancelled' THEN o.order_amount ELSE 0 END)
        / SUM(o.order_amount), 2
    )                                                            AS Revenue_Loss_Pct
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.city
ORDER BY Revenue_Lost DESC;
GO

-- ==============================================================================
-- SECTION 7: ADVANCED PRODUCT ANALYTICS
-- ==============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 21: Repeat Customer Analysis (Orders > 3)
-- ─────────────────────────────────────────────────────────────────────────────
WITH Customer_Orders AS (
    SELECT customer_id, COUNT(order_id) AS Order_Count
    FROM dbo.Orders WHERE status = 'Delivered'
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN Order_Count = 1  THEN 'One-Time Buyer'
        WHEN Order_Count BETWEEN 2 AND 5  THEN 'Occasional (2–5 orders)'
        WHEN Order_Count BETWEEN 6 AND 10 THEN 'Regular (6–10 orders)'
        ELSE 'Loyal (10+ orders)'
    END                                                          AS Customer_Segment,
    COUNT(customer_id)                                           AS Customer_Count,
    ROUND(AVG(CAST(Order_Count AS FLOAT)), 1)                    AS Avg_Orders
FROM Customer_Orders
GROUP BY
    CASE
        WHEN Order_Count = 1  THEN 'One-Time Buyer'
        WHEN Order_Count BETWEEN 2 AND 5  THEN 'Occasional (2–5 orders)'
        WHEN Order_Count BETWEEN 6 AND 10 THEN 'Regular (6–10 orders)'
        ELSE 'Loyal (10+ orders)'
    END
ORDER BY Avg_Orders;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 22: Day-of-Week Revenue Pattern
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    DATENAME(WEEKDAY, order_date)                                AS Day_of_Week,
    DATEPART(WEEKDAY, order_date)                                AS Day_Num,
    COUNT(order_id)                                              AS Total_Orders,
    ROUND(SUM(CASE WHEN status='Delivered' THEN final_amount ELSE 0 END), 2) AS Revenue,
    ROUND(AVG(CAST(delivery_time_minutes AS FLOAT)), 1)          AS Avg_Delivery_Time
FROM dbo.Orders
GROUP BY DATENAME(WEEKDAY, order_date), DATEPART(WEEKDAY, order_date)
ORDER BY Day_Num;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 23: Restaurant Prep Time vs Delivery Time Correlation
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    r.restaurant_name,
    r.average_prep_time                                          AS Avg_Prep_Time,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)), 1)        AS Avg_Delivery_Time,
    ROUND(AVG(CAST(o.delivery_time_minutes AS FLOAT)) + r.average_prep_time, 1)
                                                                 AS Estimated_Total_Wait,
    COUNT(o.order_id)                                            AS Orders
FROM dbo.Orders o
JOIN dbo.Restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'Delivered'
GROUP BY r.restaurant_name, r.average_prep_time
HAVING COUNT(o.order_id) >= 15
ORDER BY Estimated_Total_Wait DESC;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 24: Customer Acquisition Trend (Signups by Month)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    FORMAT(signup_date, 'MMM yyyy')                              AS Signup_Month,
    YEAR(signup_date)                                            AS Year,
    MONTH(signup_date)                                           AS Month,
    COUNT(customer_id)                                           AS New_Customers,
    SUM(COUNT(customer_id)) OVER (ORDER BY YEAR(signup_date), MONTH(signup_date))
                                                                 AS Cumulative_Customers
FROM dbo.Customers
WHERE signup_date IS NOT NULL
GROUP BY FORMAT(signup_date, 'MMM yyyy'), YEAR(signup_date), MONTH(signup_date)
ORDER BY Year, Month;
GO

-- ─────────────────────────────────────────────────────────────────────────────
-- Query 25: Full Funnel Summary — Orders → Delivered → Reviewed
-- ─────────────────────────────────────────────────────────────────────────────
WITH Funnel AS (
    SELECT
        COUNT(DISTINCT o.order_id)                               AS Total_Orders,
        COUNT(DISTINCT CASE WHEN o.status = 'Delivered' THEN o.order_id END)
                                                                 AS Delivered_Orders,
        COUNT(DISTINCT CASE WHEN o.status = 'Cancelled' THEN o.order_id END)
                                                                 AS Cancelled_Orders,
        COUNT(DISTINCT CASE WHEN o.status = 'Delayed' THEN o.order_id END)
                                                                 AS Delayed_Orders,
        COUNT(DISTINCT r.review_id)                              AS Reviewed_Orders
    FROM dbo.Orders o
    LEFT JOIN dbo.Reviews r ON o.order_id = r.order_id
)
SELECT
    Total_Orders,
    Delivered_Orders,
    Cancelled_Orders,
    Delayed_Orders,
    Reviewed_Orders,
    ROUND(100.0 * Delivered_Orders / Total_Orders, 2)            AS Delivery_Success_Rate,
    ROUND(100.0 * Cancelled_Orders / Total_Orders, 2)            AS Cancellation_Rate,
    ROUND(100.0 * Reviewed_Orders / NULLIF(Delivered_Orders, 0), 2)
                                                                 AS Review_Conversion_Rate
FROM Funnel;
GO