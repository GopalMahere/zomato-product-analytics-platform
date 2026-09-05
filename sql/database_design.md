# Database Design — Zomato Product Analytics Platform

## Overview

This document describes the complete relational database schema for the Zomato Product Analytics Platform, designed for **SQL Server 2022**.

---

## Entity-Relationship Diagram

```
┌──────────────┐         ┌──────────────────────┐         ┌──────────────────────┐
│  Customers   │ 1     N │       Orders         │ N     1 │    Restaurants       │
│──────────────│─────────│──────────────────────│─────────│──────────────────────│
│ customer_id  │         │ order_id (PK)        │         │ restaurant_id (PK)   │
│ customer_name│         │ customer_id (FK)     │         │ restaurant_name      │
│ age          │         │ restaurant_id (FK)   │         │ city                 │
│ gender       │         │ partner_id (FK)      │         │ cuisine              │
│ city         │         │ order_date           │         │ average_rating       │
│ signup_date  │         │ order_time           │         │ average_prep_time    │
│ zomato_gold  │         │ order_amount         │         └──────────────────────┘
└──────────────┘         │ delivery_fee         │
                         │ discount             │         ┌──────────────────────┐
                         │ final_amount         │ N     1 │  Delivery_Partners   │
                         │ payment_id           │─────────│──────────────────────│
                         │ status               │         │ partner_id (PK)      │
                         │ delivery_time_minutes│         │ partner_name         │
                         └──────────────────────┘         │ city                 │
                                  │                        │ vehicle_type         │
                     ┌────────────┴───────────┐           │ experience_years     │
                     │                        │           │ rating               │
              ┌──────▼───────┐    ┌───────────▼──────┐   └──────────────────────┘
              │   Payments   │    │     Reviews      │
              │──────────────│    │──────────────────│
              │ payment_id   │    │ review_id        │
              │ order_id(FK) │    │ order_id (FK)    │
              │ payment_method│   │ customer_id (FK) │
              │ payment_status│   │ restaurant_id(FK)│
              └──────────────┘    │ rating           │
                                  │ review_text      │
                                  └──────────────────┘
```

---

## Table Definitions

### 1. Customers (Dimension)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| customer_id | VARCHAR(20) | PK, NOT NULL | e.g. CUST00001 |
| customer_name | NVARCHAR(100) | NOT NULL | Full name |
| age | INT | CHECK (18–120) | Customer age |
| gender | VARCHAR(20) | — | Male / Female / Other |
| city | NVARCHAR(100) | — | One of 8 cities |
| signup_date | DATE | — | Registration date |
| zomato_gold | BIT | DEFAULT 0 | 1 = Gold member |

### 2. Restaurants (Dimension)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| restaurant_id | VARCHAR(20) | PK, NOT NULL | e.g. REST0001 |
| restaurant_name | NVARCHAR(200) | NOT NULL | Business name |
| city | NVARCHAR(100) | — | One of 8 cities |
| cuisine | NVARCHAR(100) | — | Cuisine type |
| average_rating | DECIMAL(3,2) | CHECK (0–5) | Platform rating |
| average_prep_time | INT | — | Minutes |

### 3. Delivery_Partners (Dimension)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| partner_id | VARCHAR(20) | PK, NOT NULL | e.g. PART0001 |
| partner_name | NVARCHAR(100) | NOT NULL | Full name |
| city | NVARCHAR(100) | — | Base city |
| vehicle_type | VARCHAR(50) | — | Bike / Scooter / Cycle |
| experience_years | INT | CHECK (>=0) | Years of experience |
| rating | DECIMAL(3,2) | CHECK (0–5) | Partner rating |

### 4. Orders (Fact)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| order_id | VARCHAR(20) | PK, NOT NULL | e.g. ORD000001 |
| customer_id | VARCHAR(20) | FK → Customers | |
| restaurant_id | VARCHAR(20) | FK → Restaurants | |
| partner_id | VARCHAR(20) | FK → Delivery_Partners | |
| order_date | DATE | — | Date of order |
| order_time | TIME(0) | — | Time of order |
| order_amount | DECIMAL(10,2) | — | Pre-discount amount |
| delivery_fee | DECIMAL(10,2) | — | Delivery charge |
| discount | DECIMAL(10,2) | — | Discount applied |
| final_amount | DECIMAL(10,2) | — | Amount paid |
| payment_id | VARCHAR(20) | — | Linked payment |
| status | VARCHAR(50) | — | Delivered / Cancelled / Delayed |
| delivery_time_minutes | INT | — | Actual delivery time |

### 5. Payments (Fact)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| payment_id | VARCHAR(20) | PK, NOT NULL | e.g. PAY000001 |
| order_id | VARCHAR(20) | FK → Orders | |
| payment_method | VARCHAR(50) | — | UPI / Card / Cash / Wallet |
| payment_status | VARCHAR(50) | — | Success / Failed / Refunded |

### 6. Reviews (Fact)

| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| review_id | VARCHAR(20) | PK, NOT NULL | e.g. REV00001 |
| order_id | VARCHAR(20) | FK → Orders | |
| customer_id | VARCHAR(20) | FK → Customers | |
| restaurant_id | VARCHAR(20) | FK → Restaurants | |
| rating | INT | CHECK (1–5) | Star rating |
| review_text | NVARCHAR(MAX) | — | Review comment |

---

## Dataset Scope

| Entity | Count |
|--------|-------|
| Customers | 2,500 |
| Restaurants | 300 |
| Delivery Partners | 150 |
| Orders | 10,000 |
| Payments | 10,000 |
| Reviews | 8,000 |
| Cities | 8 |

**Time Period**: January 2025 – December 2025

## Cities

1. Delhi
2. Mumbai
3. Bengaluru
4. Hyderabad
5. Pune
6. Chennai
7. Kolkata
8. Jaipur

## Cuisines

North Indian, South Indian, Chinese, Italian, Fast Food, Pizza, Café, Biryani, Desserts, Healthy Food