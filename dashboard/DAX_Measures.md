# DAX Measures — Zomato Product Analytics Platform

Copy these measures into Power BI Desktop. Create a dedicated **Measures Table** to keep them organized.

---

## 📦 How to Add Measures

1. In Power BI Desktop, right-click any table in the **Data** pane
2. Select **New Measure**
3. Paste the DAX formula
4. Press **Enter** to save

---

## ═══════════════════════════════════
## SECTION 1: CORE KPI MEASURES
## ═══════════════════════════════════

### Total Orders
```DAX
Total Orders = COUNTROWS(Orders)
```

### Delivered Orders
```DAX
Delivered Orders = 
CALCULATE(COUNTROWS(Orders), Orders[status] = "Delivered")
```

### Cancelled Orders
```DAX
Cancelled Orders = 
CALCULATE(COUNTROWS(Orders), Orders[status] = "Cancelled")
```

### Delayed Orders
```DAX
Delayed Orders = 
CALCULATE(COUNTROWS(Orders), Orders[status] = "Delayed")
```

### Total Revenue
```DAX
Total Revenue = 
CALCULATE(
    SUM(Orders[final_amount]),
    Orders[status] = "Delivered"
)
```

### Average Order Value (AOV)
```DAX
Avg Order Value = 
CALCULATE(
    AVERAGE(Orders[final_amount]),
    Orders[status] = "Delivered"
)
```

### Cancellation Rate %
```DAX
Cancellation Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(Orders), Orders[status] = "Cancelled"),
    COUNTROWS(Orders),
    0
) * 100
```

### Delivery Success Rate %
```DAX
Delivery Success Rate % = 
DIVIDE([Delivered Orders], [Total Orders], 0) * 100
```

### Average Delivery Time (Minutes)
```DAX
Avg Delivery Time = 
AVERAGE(Orders[delivery_time_minutes])
```

### Total Customers
```DAX
Total Customers = COUNTROWS(Customers)
```

### Total Restaurants
```DAX
Total Restaurants = COUNTROWS(Restaurants)
```

### Total Discount Given
```DAX
Total Discount = 
CALCULATE(SUM(Orders[discount]), Orders[status] = "Delivered")
```

### Net Revenue (After Discounts)
```DAX
Net Revenue = [Total Revenue]
```
> Note: `final_amount` already accounts for discounts, so this equals Total Revenue.

### Gross Revenue (Before Discounts)
```DAX
Gross Revenue = 
CALCULATE(
    SUM(Orders[order_amount]),
    Orders[status] = "Delivered"
)
```

---

## ═══════════════════════════════════
## SECTION 2: GROWTH & TREND MEASURES
## ═══════════════════════════════════

### Previous Month Revenue
```DAX
Prev Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD(DateTable[Date], -1, MONTH)
)
```

### Month-over-Month Growth %
```DAX
MoM Revenue Growth % = 
VAR CurrentRevenue = [Total Revenue]
VAR PrevRevenue = [Prev Month Revenue]
RETURN
DIVIDE(CurrentRevenue - PrevRevenue, PrevRevenue, 0) * 100
```

### Revenue YTD
```DAX
Revenue YTD = 
TOTALYTD([Total Revenue], DateTable[Date])
```

### Orders YTD
```DAX
Orders YTD = 
TOTALYTD([Total Orders], DateTable[Date])
```

### Running Total Revenue
```DAX
Running Total Revenue = 
CALCULATE(
    [Total Revenue],
    FILTER(
        ALL(DateTable),
        DateTable[Date] <= MAX(DateTable[Date])
    )
)
```

---

## ═══════════════════════════════════
## SECTION 3: CUSTOMER ANALYTICS
## ═══════════════════════════════════

### Gold Members Count
```DAX
Gold Members = 
CALCULATE(COUNTROWS(Customers), Customers[zomato_gold] = 1)
```

### Gold Members %
```DAX
Gold Members % = 
DIVIDE([Gold Members], [Total Customers], 0) * 100
```

### Gold Member Revenue
```DAX
Gold Member Revenue = 
CALCULATE(
    [Total Revenue],
    FILTER(Customers, Customers[zomato_gold] = 1)
)
```

### Regular Member Revenue
```DAX
Regular Member Revenue = 
CALCULATE(
    [Total Revenue],
    FILTER(Customers, Customers[zomato_gold] = 0)
)
```

### Gold vs Regular AOV Ratio
```DAX
Gold AOV = 
CALCULATE(
    [Avg Order Value],
    FILTER(Customers, Customers[zomato_gold] = 1)
)
```

```DAX
Regular AOV = 
CALCULATE(
    [Avg Order Value],
    FILTER(Customers, Customers[zomato_gold] = 0)
)
```

### Avg Orders Per Customer
```DAX
Avg Orders Per Customer = 
DIVIDE([Delivered Orders], [Total Customers], 0)
```

### Unique Ordering Customers
```DAX
Active Customers = 
DISTINCTCOUNT(Orders[customer_id])
```

---

## ═══════════════════════════════════
## SECTION 4: DELIVERY OPERATIONS
## ═══════════════════════════════════

### SLA Breach Count (>30 min)
```DAX
SLA Breached Orders = 
CALCULATE(
    COUNTROWS(Orders),
    Orders[delivery_time_minutes] > 30,
    Orders[status] = "Delivered"
)
```

### SLA Breach Rate %
```DAX
SLA Breach Rate % = 
DIVIDE([SLA Breached Orders], [Delivered Orders], 0) * 100
```

### SLA Compliance Rate %
```DAX
SLA Compliance Rate % = 100 - [SLA Breach Rate %]
```

### On-Time Deliveries
```DAX
On-Time Deliveries = 
CALCULATE(
    COUNTROWS(Orders),
    Orders[delivery_time_minutes] <= 30,
    Orders[status] = "Delivered"
)
```

### Fastest Delivery Time
```DAX
Fastest Delivery = 
CALCULATE(
    MIN(Orders[delivery_time_minutes]),
    Orders[status] = "Delivered"
)
```

### Slowest Delivery Time
```DAX
Slowest Delivery = 
CALCULATE(
    MAX(Orders[delivery_time_minutes]),
    Orders[status] = "Delivered"
)
```

---

## ═══════════════════════════════════
## SECTION 5: PAYMENT ANALYTICS
## ═══════════════════════════════════

### Payment Success Count
```DAX
Successful Payments = 
CALCULATE(COUNTROWS(Payments), Payments[payment_status] = "Success")
```

### Payment Failure Rate %
```DAX
Payment Failure Rate % = 
DIVIDE(
    CALCULATE(COUNTROWS(Payments), Payments[payment_status] = "Failed"),
    COUNTROWS(Payments),
    0
) * 100
```

### Total Refunded
```DAX
Total Refunded Orders = 
CALCULATE(COUNTROWS(Payments), Payments[payment_status] = "Refunded")
```

---

## ═══════════════════════════════════
## SECTION 6: RESTAURANT METRICS
## ═══════════════════════════════════

### Avg Restaurant Rating
```DAX
Avg Restaurant Rating = AVERAGE(Restaurants[average_rating])
```

### Total Reviews
```DAX
Total Reviews = COUNTROWS(Reviews)
```

### Avg Review Rating
```DAX
Avg Review Rating = AVERAGE(Reviews[rating])
```

### Positive Reviews %
```DAX
Positive Reviews % = 
DIVIDE(
    CALCULATE(COUNTROWS(Reviews), Reviews[rating] >= 4),
    COUNTROWS(Reviews),
    0
) * 100
```

### Negative Reviews %
```DAX
Negative Reviews % = 
DIVIDE(
    CALCULATE(COUNTROWS(Reviews), Reviews[rating] <= 2),
    COUNTROWS(Reviews),
    0
) * 100
```

### Revenue per Restaurant
```DAX
Revenue per Restaurant = 
DIVIDE([Total Revenue], [Total Restaurants], 0)
```

---

## ═══════════════════════════════════
## SECTION 7: REVENUE INTELLIGENCE
## ═══════════════════════════════════

### Revenue Lost to Cancellations
```DAX
Revenue Lost (Cancellations) = 
CALCULATE(
    SUM(Orders[order_amount]),
    Orders[status] = "Cancelled"
)
```

### Avg Discount %
```DAX
Avg Discount % = 
DIVIDE(
    CALCULATE(SUM(Orders[discount]), Orders[status] = "Delivered"),
    CALCULATE(SUM(Orders[order_amount]), Orders[status] = "Delivered"),
    0
) * 100
```

### Revenue per Customer
```DAX
Revenue per Customer = 
DIVIDE([Total Revenue], [Active Customers], 0)
```

### Revenue per Order
```DAX
Revenue per Order = 
DIVIDE([Total Revenue], [Delivered Orders], 0)
```

---

## Quick Reference Card

| Measure | Value Type | Usage |
|---------|-----------|-------|
| Total Orders | Count | KPI Card |
| Total Revenue | Currency ₹ | KPI Card, Trend |
| Avg Order Value | Currency ₹ | KPI Card |
| Cancellation Rate % | Percentage | KPI Card, Alert |
| SLA Breach Rate % | Percentage | Gauge, KPI |
| MoM Growth % | Percentage | Trend |
| Gold Members % | Percentage | Demographics |
| Payment Failure Rate % | Percentage | Operations |
| Positive Reviews % | Percentage | Sentiment |
