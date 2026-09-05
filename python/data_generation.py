import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
from faker import Faker

# Constants and Configurations
DATA_DIR = "data/raw"
NUM_CUSTOMERS = 2500
NUM_RESTAURANTS = 300
NUM_ORDERS = 10000
NUM_PARTNERS = 150
NUM_REVIEWS = 8000

CITIES = [
    "Delhi", "Mumbai", "Bengaluru", "Hyderabad", 
    "Pune", "Chennai", "Kolkata", "Jaipur"
]

CUISINES = [
    "North Indian", "South Indian", "Chinese", "Italian", 
    "Fast Food", "Pizza", "Cafe", "Biryani", "Desserts", "Healthy Food"
]

VEHICLES = ["Bike", "Scooter", "Cycle"]

ORDER_STATUS = ["Delivered", "Cancelled", "Delayed"]
ORDER_STATUS_PROBS = [0.8, 0.1, 0.1]

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Wallet"]
PAYMENT_STATUSES = ["Success", "Failed", "Refunded"]
PAYMENT_STATUS_PROBS = [0.90, 0.05, 0.05]

REVIEW_TEXTS = [
    "Amazing food", "Very late delivery", "Worth the money", 
    "Packaging was poor", "Would order again", "Excellent taste", 
    "Delivery was delayed", "Average experience", "Loved it", "Not satisfied"
]

def setup_environment():
    """Sets random seeds and creates necessary directories."""
    random.seed(42)
    np.random.seed(42)
    Faker.seed(42)
    os.makedirs(DATA_DIR, exist_ok=True)

def generate_customers(fake: Faker) -> pd.DataFrame:
    """Generates synthetic customer data."""
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "customer_id": f"CUST{i:05d}",
            "customer_name": fake.name(),
            "age": random.randint(18, 60),
            "gender": random.choice(["Male", "Female", "Other"]),
            "city": random.choice(CITIES),
            "signup_date": fake.date_between(start_date="-3y", end_date="today"),
            "zomato_gold": random.choice([True, False])
        })
    return pd.DataFrame(customers)

def generate_restaurants(fake: Faker) -> pd.DataFrame:
    """Generates synthetic restaurant data."""
    restaurants = []
    for i in range(1, NUM_RESTAURANTS + 1):
        restaurants.append({
            "restaurant_id": f"REST{i:04d}",
            "restaurant_name": fake.company() + " Restaurant",
            "city": random.choice(CITIES),
            "cuisine": random.choice(CUISINES),
            "average_rating": round(random.uniform(3.0, 5.0), 1),
            "average_prep_time": random.randint(15, 60)
        })
    return pd.DataFrame(restaurants)

def generate_delivery_partners(fake: Faker) -> pd.DataFrame:
    """Generates synthetic delivery partner data."""
    partners = []
    for i in range(1, NUM_PARTNERS + 1):
        partners.append({
            "partner_id": f"PART{i:04d}",
            "partner_name": fake.name(),
            "city": random.choice(CITIES),
            "vehicle_type": random.choice(VEHICLES),
            "experience_years": random.randint(0, 5),
            "rating": round(random.uniform(3.5, 5.0), 1)
        })
    return pd.DataFrame(partners)

def generate_orders_and_payments(fake: Faker, customers_df: pd.DataFrame, 
                                 restaurants_df: pd.DataFrame, partners_df: pd.DataFrame):
    """Generates interrelated orders and payments data."""
    orders = []
    payments = []
    
    customer_ids = customers_df["customer_id"].tolist()
    restaurant_ids = restaurants_df["restaurant_id"].tolist()
    partner_ids = partners_df["partner_id"].tolist()
    
    for i in range(1, NUM_ORDERS + 1):
        order_id = f"ORD{i:06d}"
        payment_id = f"PAY{i:06d}"
        
        # Temporal data
        order_dt = fake.date_time_between(start_date="-1y", end_date="now")
        
        # Financial data
        order_amount = random.randint(150, 2000)
        delivery_fee = random.randint(20, 100)
        discount = random.randint(0, int(order_amount * 0.3))
        final_amount = order_amount + delivery_fee - discount
        
        status = np.random.choice(ORDER_STATUS, p=ORDER_STATUS_PROBS)
        
        # Build Order
        orders.append({
            "order_id": order_id,
            "customer_id": random.choice(customer_ids),
            "restaurant_id": random.choice(restaurant_ids),
            "partner_id": random.choice(partner_ids),
            "order_date": order_dt.date(),
            "order_time": order_dt.time().strftime("%H:%M:%S"),
            "order_amount": order_amount,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "final_amount": final_amount,
            "payment_id": payment_id,
            "status": status,
            "delivery_time_minutes": random.randint(15, 90)
        })
        
        # Build Payment (Logic ensures failed payments mostly happen on cancelled orders, but maintains randomness)
        payment_status = "Success"
        if status == "Cancelled":
            payment_status = random.choice(["Refunded", "Failed"])
        else:
            payment_status = np.random.choice(PAYMENT_STATUSES, p=PAYMENT_STATUS_PROBS)

        payments.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_method": random.choice(PAYMENT_METHODS),
            "payment_status": payment_status
        })
        
    return pd.DataFrame(orders), pd.DataFrame(payments)

def generate_reviews(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Generates synthetic reviews referencing valid orders."""
    # Select random subset of orders to have reviews (not all orders get reviewed)
    sampled_orders = orders_df.sample(n=NUM_REVIEWS, random_state=42).reset_index(drop=True)
    
    reviews = []
    for idx, row in sampled_orders.iterrows():
        reviews.append({
            "review_id": f"REV{idx + 1:05d}",
            "order_id": row["order_id"],
            "customer_id": row["customer_id"],
            "restaurant_id": row["restaurant_id"],
            "rating": random.randint(1, 5),
            "review_text": random.choice(REVIEW_TEXTS)
        })
        
    return pd.DataFrame(reviews)

def main():
    print("Starting Zomato Dataset Generation...")
    setup_environment()
    
    # Initialize Faker with Indian locale
    fake = Faker('en_IN')
    
    # 1. Generate core entities
    print("Generating Customers...")
    df_customers = generate_customers(fake)
    
    print("Generating Restaurants...")
    df_restaurants = generate_restaurants(fake)
    
    print("Generating Delivery Partners...")
    df_partners = generate_delivery_partners(fake)
    
    # 2. Generate transactional entities
    print("Generating Orders and Payments...")
    df_orders, df_payments = generate_orders_and_payments(
        fake, df_customers, df_restaurants, df_partners
    )
    
    print("Generating Reviews...")
    df_reviews = generate_reviews(df_orders)
    
    # 3. Save datasets
    datasets = {
        "customers.csv": df_customers,
        "restaurants.csv": df_restaurants,
        "delivery_partners.csv": df_partners,
        "orders.csv": df_orders,
        "payments.csv": df_payments,
        "reviews.csv": df_reviews
    }
    
    print("\n--- Dataset Shapes ---")
    for filename, df in datasets.items():
        filepath = os.path.join(DATA_DIR, filename)
        df.to_csv(filepath, index=False)
        print(f"{filename:<22}: {df.shape}")
        
    print("\nDataset Generation Completed Successfully")

if __name__ == "__main__":
    main()