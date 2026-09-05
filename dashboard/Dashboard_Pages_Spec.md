# Dashboard Pages Specification

## Zomato Product Analytics Platform — Power BI Dashboard

5-page interactive dashboard covering all major business domains.

---

## Page 1: Executive Overview

**Purpose**: High-level snapshot for C-suite and leadership

### KPI Cards (Top Row — 6 cards)
| KPI | Measure | Format | Color |
|-----|---------|--------|-------|
| Total Orders | `[Total Orders]` | 10,000 | Blue |
| Total Revenue | `[Total Revenue]` | ₹X,XX,XXX | Green |
| Avg Order Value | `[Avg Order Value]` | ₹XXX | Orange |
| Cancellation Rate | `[Cancellation Rate %]` | XX.X% | Red alert |
| SLA Breach Rate | `[SLA Breach Rate %]` | XX.X% | Yellow |
| Avg Delivery Time | `[Avg Delivery Time]` | XX min | Purple |

### Main Visuals
| Visual | Type | X-Axis | Y-Axis | Color |
|--------|------|--------|--------|-------|
| Monthly Revenue Trend | Area Line Chart | Month | Total Revenue | #E23744 |
| Order Status Split | Donut Chart | — | Status Count | Delivered=Green, Cancelled=Red, Delayed=Orange |
| Revenue by City | Horizontal Bar | City | Revenue | Gradient red |
| Order Funnel | Funnel Chart | Stage | Count | Multi-color |

### Slicers
- Year (dropdown)
- City (multi-select)
- Date range picker

---

## Page 2: Customer Analytics

**Purpose**: Understand who your customers are and how they behave

### KPI Cards (Top Row — 4 cards)
| KPI | Measure |
|-----|---------|
| Total Customers | `[Total Customers]` |
| Active Customers | `[Active Customers]` |
| Gold Members % | `[Gold Members %]` |
| Avg Revenue Per Customer | `[Revenue per Customer]` |

### Main Visuals
| Visual | Type | Details |
|--------|------|---------|
| Gold vs Regular Comparison | Clustered Bar | AOV, Total Orders, Revenue side by side |
| Age Distribution | Histogram (Column Chart) | Age buckets 18–25, 26–35, 36–45, 46–60 |
| Gender Split | Pie Chart | Male / Female / Other |
| CLV Segments | Stacked Bar | High Value / Mid / Low / At Risk |
| Customer Cohort Retention | Matrix Heatmap | Rows=Cohort Month, Cols=Month 0–6, Values=Active % |
| Signup Trend | Line Chart | Monthly new customer acquisitions |

### Slicers
- Gender
- City
- Gold Member (Yes/No)
- Age Range

---

## Page 3: Restaurant Performance

**Purpose**: Identify top restaurants, cuisine trends, and rating patterns

### KPI Cards (Top Row — 4 cards)
| KPI | Measure |
|-----|---------|
| Total Restaurants | `[Total Restaurants]` |
| Avg Restaurant Rating | `[Avg Restaurant Rating]` |
| Total Reviews | `[Total Reviews]` |
| Positive Reviews % | `[Positive Reviews %]` |

### Main Visuals
| Visual | Type | Details |
|--------|------|---------|
| Top 10 Restaurants by Revenue | Horizontal Bar | Restaurant Name vs Revenue, colored by city |
| Revenue by Cuisine | Treemap | Size=Revenue, Color=Cuisine |
| Rating vs Revenue Scatter | Scatter Chart | X=Avg Rating, Y=Revenue, Size=Order Count |
| Cuisine by City | Stacked Bar | X=City, Y=Orders, Color=Cuisine |
| Restaurant Ratings Distribution | Column Chart | X=Rating Bucket, Y=Count |
| Top Restaurants Table | Table | Name, City, Cuisine, Revenue, Avg Rating, Orders, Reviews |

### Slicers
- City
- Cuisine
- Rating range (3.0–5.0)

---

## Page 4: Delivery Operations

**Purpose**: Monitor delivery efficiency, SLA compliance, and partner performance

### KPI Cards (Top Row — 5 cards)
| KPI | Measure |
|-----|---------|
| Avg Delivery Time | `[Avg Delivery Time]` min |
| SLA Compliance Rate | `[SLA Compliance Rate %]` |
| SLA Breach Rate | `[SLA Breach Rate %]` |
| Fastest Delivery | `[Fastest Delivery]` min |
| Total Delivery Partners | `COUNTROWS(Delivery_Partners)` |

### Main Visuals
| Visual | Type | Details |
|--------|------|---------|
| SLA Compliance Gauge | Gauge | Value=[SLA Compliance Rate %], Target=80% |
| Avg Delivery Time by Vehicle | Clustered Column | Bike vs Scooter vs Cycle |
| Hourly Order Volume | Line Chart | X=Hour (0–23), Y=Total Orders — shows peak hours |
| Cancellation Rate by City | Horizontal Bar | Color coded by severity |
| SLA Breach by City | Heatmap / Matrix | City vs SLA Breach % |
| Top Delivery Partners | Table | Name, City, Vehicle, Rating, Deliveries, Avg Time |
| Delivery Time Distribution | Histogram | Column chart with 30-min SLA reference line |

### Slicers
- City
- Vehicle Type
- Month

---

## Page 5: Payment & Revenue

**Purpose**: Understand payment behavior, failures, and revenue optimization

### KPI Cards (Top Row — 5 cards)
| KPI | Measure |
|-----|---------|
| Total Payments | `COUNTROWS(Payments)` |
| Payment Failure Rate | `[Payment Failure Rate %]` |
| Total Discounts Given | `[Total Discount]` |
| Revenue Lost (Cancellations) | `[Revenue Lost (Cancellations)]` |
| Avg Discount % | `[Avg Discount %]` |

### Main Visuals
| Visual | Type | Details |
|--------|------|---------|
| Payment Method Usage | Bar Chart | X=Method, Y=Count — UPI, Card, Cash, Wallet, Debit |
| Payment Status Split | Donut Chart | Success=Green, Failed=Red, Refunded=Orange |
| Revenue vs Discounts | Dual-axis Line Chart | Revenue line + Discount area by month |
| Payment Method × Status | Matrix | Rows=Method, Cols=Status, Values=Count |
| Revenue Waterfall | Waterfall Chart | Gross → Discounts → Cancelled → Net Revenue |
| Failure Rate by Method | Column Chart | Which payment method fails most |

### Slicers
- Payment Method
- Payment Status
- Month
- City

---

## Dashboard Design System

### Color Palette
```
Primary Red:    #E23744  (Zomato brand red)
Orange:         #FF6B35
Yellow/Gold:    #FFC20E
Green:          #4CAF50
Blue:           #2196F3
Purple:         #9C27B0
Background:     #1a1a2e
Card BG:        #16213e
Text Primary:   #FFFFFF
Text Secondary: #B0B0B0
```

### Typography
- **Title**: Segoe UI, Bold, 18pt
- **KPI Value**: Segoe UI, Bold, 28pt
- **KPI Label**: Segoe UI, Regular, 12pt
- **Body**: Segoe UI, Regular, 11pt

### Layout Rules
- Page size: 1920 × 1080 (16:9 widescreen)
- Top navigation bar: 60px height
- KPI card row: 120px height
- Padding: 12px between all visuals
- Card corners: 8px rounded

### Interactivity
- All visuals should cross-filter each other
- Add drill-through from Restaurant Name to Restaurant Detail page
- Add tooltips showing additional metrics on hover
- Add conditional formatting on cancellation rate (Red if >12%)
