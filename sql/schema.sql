-- ==============================================================================
-- Database Schema for Zomato Product Analytics Platform
-- Target DBMS: SQL Server 2022
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. DROP EXISTING TABLES (Reverse Dependency Order)
-- ------------------------------------------------------------------------------
-- This ensures that if you re-run the script, it safely drops tables 
-- without violating foreign key constraints.
IF OBJECT_ID('dbo.Reviews', 'U') IS NOT NULL DROP TABLE dbo.Reviews;
IF OBJECT_ID('dbo.Payments', 'U') IS NOT NULL DROP TABLE dbo.Payments;
IF OBJECT_ID('dbo.Orders', 'U') IS NOT NULL DROP TABLE dbo.Orders;
IF OBJECT_ID('dbo.Delivery_Partners', 'U') IS NOT NULL DROP TABLE dbo.Delivery_Partners;
IF OBJECT_ID('dbo.Restaurants', 'U') IS NOT NULL DROP TABLE dbo.Restaurants;
IF OBJECT_ID('dbo.Customers', 'U') IS NOT NULL DROP TABLE dbo.Customers;
GO

-- ------------------------------------------------------------------------------
-- 2. CREATE DIMENSION TABLES
-- ------------------------------------------------------------------------------

-- Customers Table
CREATE TABLE dbo.Customers (
    customer_id VARCHAR(20) NOT NULL,
    customer_name NVARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(20),
    city NVARCHAR(100),
    signup_date DATE,
    zomato_gold BIT DEFAULT 0,  -- BIT maps to True/False or 1/0
    
    CONSTRAINT PK_Customers PRIMARY KEY (customer_id),
    CONSTRAINT CHK_Customer_Age CHECK (age >= 18 AND age <= 120)
);
GO

-- Restaurants Table
CREATE TABLE dbo.Restaurants (
    restaurant_id VARCHAR(20) NOT NULL,
    restaurant_name NVARCHAR(200) NOT NULL,
    city NVARCHAR(100),
    cuisine NVARCHAR(100),
    average_rating DECIMAL(3, 2),
    average_prep_time INT,
    
    CONSTRAINT PK_Restaurants PRIMARY KEY (restaurant_id),
    CONSTRAINT CHK_Rest_Rating CHECK (average_rating >= 0.0 AND average_rating <= 5.0)
);
GO

-- Delivery Partners Table
CREATE TABLE dbo.Delivery_Partners (
    partner_id VARCHAR(20) NOT NULL,
    partner_name NVARCHAR(100) NOT NULL,
    city NVARCHAR(100),
    vehicle_type VARCHAR(50),
    experience_years INT,
    rating DECIMAL(3, 2),
    
    CONSTRAINT PK_Delivery_Partners PRIMARY KEY (partner_id),
    CONSTRAINT CHK_Partner_Rating CHECK (rating >= 0.0 AND rating <= 5.0),
    CONSTRAINT CHK_Experience CHECK (experience_years >= 0)
);
GO

-- ------------------------------------------------------------------------------
-- 3. CREATE FACT TABLES
-- ------------------------------------------------------------------------------

-- Orders Table
-- Core transactional table linking customers, restaurants, and partners.
CREATE TABLE dbo.Orders (
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_id VARCHAR(20) NOT NULL,
    partner_id VARCHAR(20) NOT NULL,
    order_date DATE,
    order_time TIME(0), -- (0) removes fractional seconds, perfectly matching the Python string output
    order_amount DECIMAL(10, 2),
    delivery_fee DECIMAL(10, 2),
    discount DECIMAL(10, 2),
    final_amount DECIMAL(10, 2),
    payment_id VARCHAR(20),
    status VARCHAR(50),
    delivery_time_minutes INT,
    
    CONSTRAINT PK_Orders PRIMARY KEY (order_id),
    CONSTRAINT FK_Orders_Customers FOREIGN KEY (customer_id) REFERENCES dbo.Customers(customer_id),
    CONSTRAINT FK_Orders_Restaurants FOREIGN KEY (restaurant_id) REFERENCES dbo.Restaurants(restaurant_id),
    CONSTRAINT FK_Orders_Partners FOREIGN KEY (partner_id) REFERENCES dbo.Delivery_Partners(partner_id)
);
GO

-- Payments Table
CREATE TABLE dbo.Payments (
    payment_id VARCHAR(20) NOT NULL,
    order_id VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    
    CONSTRAINT PK_Payments PRIMARY KEY (payment_id),
    CONSTRAINT FK_Payments_Orders FOREIGN KEY (order_id) REFERENCES dbo.Orders(order_id)
);
GO

-- Reviews Table
CREATE TABLE dbo.Reviews (
    review_id VARCHAR(20) NOT NULL,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_id VARCHAR(20) NOT NULL,
    rating INT,
    review_text NVARCHAR(MAX),
    
    CONSTRAINT PK_Reviews PRIMARY KEY (review_id),
    CONSTRAINT FK_Reviews_Orders FOREIGN KEY (order_id) REFERENCES dbo.Orders(order_id),
    CONSTRAINT FK_Reviews_Customers FOREIGN KEY (customer_id) REFERENCES dbo.Customers(customer_id),
    CONSTRAINT FK_Reviews_Restaurants FOREIGN KEY (restaurant_id) REFERENCES dbo.Restaurants(restaurant_id),
    CONSTRAINT CHK_Review_Rating CHECK (rating >= 1 AND rating <= 5)
);
GO