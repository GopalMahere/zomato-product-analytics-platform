# Power BI Dashboard — Setup Guide

## Zomato Product Analytics Platform

This guide walks you through connecting Power BI Desktop to your SQL Server database and building the 5-page executive dashboard.

---

## Prerequisites

- ✅ Power BI Desktop installed (free from Microsoft)
- ✅ SQL Server 2022 running with `Zomato_Product_Analytics` database
- ✅ Data imported via `python/import_to_sql.py`

---

## Step 1: Connect to SQL Server

1. Open **Power BI Desktop**
2. Click **Home → Get Data → SQL Server**
3. Enter:
   - **Server**: `localhost\TEW_SQLExpress` (or your server name)
   - **Database**: `Zomato_Product_Analytics`
   - **Data Connectivity mode**: `Import`
4. Click **OK → Windows Authentication → Connect**
5. In the Navigator, select all 6 tables:
   - ✅ dbo.Customers
   - ✅ dbo.Restaurants
   - ✅ dbo.Delivery_Partners
   - ✅ dbo.Orders
   - ✅ dbo.Payments
   - ✅ dbo.Reviews
6. Click **Load**

---

## Step 2: Configure the Data Model

Go to **Model View** and set up these relationships (should auto-detect most):

| From Table | Column | To Table | Column | Type |
|-----------|--------|----------|--------|------|
| Orders | customer_id | Customers | customer_id | Many-to-One |
| Orders | restaurant_id | Restaurants | restaurant_id | Many-to-One |
| Orders | partner_id | Delivery_Partners | partner_id | Many-to-One |
| Payments | order_id | Orders | order_id | One-to-One |
| Reviews | order_id | Orders | order_id | Many-to-One |
| Reviews | customer_id | Customers | customer_id | Many-to-One |
| Reviews | restaurant_id | Restaurants | restaurant_id | Many-to-One |

---

## Step 3: Create a Date Table

In **Table Tools → New Table**, paste:

```DAX
DateTable = 
ADDCOLUMNS(
    CALENDAR(DATE(2025,1,1), DATE(2025,12,31)),
    "Year",       YEAR([Date]),
    "Month",      MONTH([Date]),
    "MonthName",  FORMAT([Date], "MMM"),
    "Quarter",    "Q" & FORMAT([Date], "Q"),
    "WeekDay",    FORMAT([Date], "ddd"),
    "DayOfWeek",  WEEKDAY([Date], 2)
)
```

Then link: `DateTable[Date]` → `Orders[order_date]` (Many-to-One)

---

## Step 4: Add All DAX Measures

See `DAX_Measures.md` for all measures. Create a **Measures Table**:
- New Table → `MeasuresTable = {""}`
- Add each measure from `DAX_Measures.md` to this table

---

## Step 5: Build the Dashboard Pages

### Page 1 — Executive Overview

**Layout:**
- Top row: 6 KPI Cards
  - Total Orders, Total Revenue, Avg Order Value, Cancellation Rate, SLA Breach %, Avg Delivery Time
- Middle: Line chart — Monthly Revenue Trend (x: MonthName, y: Revenue)
- Bottom left: Donut chart — Order Status (Delivered/Cancelled/Delayed)
- Bottom right: Bar chart — Revenue by City

**Slicers (top):** Year filter, City filter, Order Status filter

---

### Page 2 — Customer Analytics

**Layout:**
- Top row: 3 KPI Cards — Total Customers, Gold Members %, Avg Customer Spend
- Left: Clustered bar — Gold vs Regular (AOV, Total Orders, Revenue)
- Middle: Pie chart — Gender Distribution
- Right: Histogram — Age Distribution (use bins)
- Bottom: Matrix — Customer Cohort Retention (Month 0–6)
- Bottom right: Stacked bar — CLV Segments

---

### Page 3 — Restaurant Performance

**Layout:**
- Top row: Total Restaurants, Avg Restaurant Rating, Best Cuisine by Revenue
- Left: Horizontal bar — Top 10 Restaurants by Revenue
- Middle: Treemap — Revenue by Cuisine
- Right: Scatter plot — Rating vs Revenue (one dot per restaurant)
- Bottom: Table — Top 20 Restaurants (Name, City, Cuisine, Revenue, Avg Rating, Orders)

---

### Page 4 — Delivery Operations

**Layout:**
- Top row: Avg Delivery Time, SLA Breach Rate, Top Vehicle Type
- Left: Clustered column — Avg Delivery Time by Vehicle Type
- Middle: Line chart — Hourly Order Volume (0–23 hours)
- Right: Gauge — SLA Compliance (target 70% on-time)
- Bottom left: Bar chart — Cancellation Rate by City
- Bottom right: Scatter plot — Partner Rating vs Avg Delivery Time

---

### Page 5 — Payment & Revenue

**Layout:**
- Top row: Total Payments, Payment Failure Rate, Total Discounts Given
- Left: Bar chart — Payment Method Usage
- Middle: Donut chart — Payment Status (Success/Failed/Refunded)
- Right: Line chart — Revenue Trend with Discount Overlay
- Bottom: Waterfall chart — Revenue Breakdown (Orders - Cancellations - Discounts = Net Revenue)
- Bottom right: Matrix — Payment Method × Status cross-tab

---

## Step 6: Publish to Power BI Service (Optional)

1. Click **Home → Publish**
2. Sign into your Power BI account
3. Select your workspace
4. Access the dashboard at `app.powerbi.com`

---

## Tips for a Professional Look

- **Theme**: Use a dark theme (View → Themes → Monokai or Nova)
- **Colors**: Primary `#E23744` (Zomato Red), Accent `#FF6B35`, Background `#1a1a2e`
- **Fonts**: Use Segoe UI throughout
- **Borders**: Add 2px rounded borders to all cards
- **Logo**: Add Zomato logo in top-left corner of each page
- **Page navigation**: Add navigation buttons between pages
