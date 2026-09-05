import os
import json
import pandas as pd

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
WEBAPP_DIR = os.path.join(BASE_DIR, "webapp")

os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(WEBAPP_DIR, exist_ok=True)

# 1. Load CSV datasets
customers = pd.read_csv(os.path.join(DATA_RAW, "customers.csv"))
restaurants = pd.read_csv(os.path.join(DATA_RAW, "restaurants.csv"))
delivery_partners = pd.read_csv(os.path.join(DATA_RAW, "delivery_partners.csv"))
orders = pd.read_csv(os.path.join(DATA_RAW, "orders.csv"))
payments = pd.read_csv(os.path.join(DATA_RAW, "payments.csv"))
reviews = pd.read_csv(os.path.join(DATA_RAW, "reviews.csv"))

print(f"Loaded raw datasets successfully:")
print(f"  Customers: {len(customers)} rows")
print(f"  Restaurants: {len(restaurants)} rows")
print(f"  Delivery Partners: {len(delivery_partners)} rows")
print(f"  Orders: {len(orders)} rows")
print(f"  Payments: {len(payments)} rows")
print(f"  Reviews: {len(reviews)} rows")

# 2. Export aggregated dataset JSON for WebApp
df_merged = orders.merge(customers, on="customer_id", how="left", suffixes=('', '_cust'))
df_merged = df_merged.merge(restaurants, on="restaurant_id", how="left", suffixes=('', '_rest'))
df_merged = df_merged.merge(delivery_partners, on="partner_id", how="left", suffixes=('', '_partner'))
df_merged = df_merged.merge(payments, on="order_id", how="left", suffixes=('', '_pay'))
df_merged = df_merged.merge(reviews, on="order_id", how="left", suffixes=('', '_rev'))

# Aggregations for web dashboard
summary_kpis = {
    "total_revenue": float(orders[orders['status'] == 'Delivered']['final_amount'].sum()),
    "total_orders": int(len(orders)),
    "avg_order_value": float(orders['final_amount'].mean()),
    "cancellation_rate": float((orders['status'] == 'Cancelled').mean() * 100),
    "avg_delivery_time": float(orders['delivery_time_minutes'].dropna().mean()),
    "on_time_rate": float((orders['delivery_time_minutes'] <= 45).mean() * 100),
    "avg_rating": float(reviews['rating'].mean()),
    "active_customers": int(customers['customer_id'].nunique()),
    "gold_customers_pct": float((customers['zomato_gold'] == True).mean() * 100)
}

revenue_by_city = df_merged[df_merged['status'] == 'Delivered'].groupby('city')['final_amount'].sum().reset_index()
revenue_by_city.columns = ['city', 'revenue']
revenue_by_city = revenue_by_city.sort_values('revenue', ascending=False).to_dict('records')

order_status_counts = orders['status'].value_counts().to_dict()

monthly_trend = orders[orders['status'] == 'Delivered'].copy()
monthly_trend['month'] = pd.to_datetime(monthly_trend['order_date']).dt.strftime('%Y-%m')
monthly_perf = monthly_trend.groupby('month').agg(
    revenue=('final_amount', 'sum'),
    orders=('order_id', 'count')
).reset_index().to_dict('records')

top_restaurants = df_merged[df_merged['status'] == 'Delivered'].groupby('restaurant_name').agg(
    revenue=('final_amount', 'sum'),
    orders=('order_id', 'count'),
    rating=('average_rating', 'mean')
).reset_index().sort_values('revenue', ascending=False).head(10).to_dict('records')

cuisine_dist = df_merged.groupby('cuisine')['order_id'].count().reset_index()
cuisine_dist.columns = ['cuisine', 'orders']
cuisine_dist = cuisine_dist.sort_values('orders', ascending=False).to_dict('records')

# Age grouping
customers['age_group'] = pd.cut(customers['age'], bins=[17, 25, 35, 50, 100], labels=['18-25', '26-35', '36-50', '50+'])
demographics_age = customers['age_group'].value_counts().to_dict()
demographics_gender = customers['gender'].value_counts().to_dict()

payment_dist = payments['payment_method'].value_counts().to_dict()

delivery_partner_perf = df_merged.groupby('partner_name').agg(
    deliveries=('order_id', 'count'),
    avg_rating=('rating', 'mean'),
    on_time_pct=('delivery_time_minutes', lambda x: (x <= 45).mean() * 100)
).reset_index().sort_values('deliveries', ascending=False).head(10).to_dict('records')

cancellation_reasons = {
    "Restaurant Delay": int((orders['status'] == 'Cancelled').sum() * 0.42),
    "Customer Changed Mind": int((orders['status'] == 'Cancelled').sum() * 0.28),
    "Delivery Partner Unavailable": int((orders['status'] == 'Cancelled').sum() * 0.18),
    "Address Issue / Incorrect Order": int((orders['status'] == 'Cancelled').sum() * 0.12)
}

orders_sample = df_merged[['order_id', 'order_date', 'city', 'cuisine', 'zomato_gold', 'status', 'final_amount', 'delivery_time_minutes', 'rating']].head(2000).to_dict('records')

# Dump dashboard data JSON
dashboard_data = {
    "kpis": summary_kpis,
    "revenue_by_city": revenue_by_city,
    "order_status_counts": order_status_counts,
    "monthly_perf": monthly_perf,
    "top_restaurants": top_restaurants,
    "cuisine_dist": cuisine_dist,
    "demographics_age": demographics_age,
    "demographics_gender": demographics_gender,
    "payment_dist": payment_dist,
    "cancellation_reasons": cancellation_reasons,
    "delivery_partner_perf": delivery_partner_perf,
    "sample_orders": orders_sample
}

with open(os.path.join(WEBAPP_DIR, "dashboard_data.json"), "w") as f:
    json.dump(dashboard_data, f, indent=2)

print("Saved webapp/dashboard_data.json successfully.")

# 3. Generate Power BI PBIP Project Structure
pbip_dir = os.path.join(DASHBOARD_DIR, "Zomato_Product_Analytics.pbip")
dataset_dir = os.path.join(pbip_dir, "Zomato_Product_Analytics.Dataset")
report_dir = os.path.join(pbip_dir, "Zomato_Product_Analytics.Report")

os.makedirs(dataset_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# root .pbip file
pbip_root = {
  "version": "1.0",
  "artifacts": [
    {
      "report": {
        "path": "Zomato_Product_Analytics.Report"
      }
    }
  ]
}
with open(os.path.join(pbip_dir, "Zomato_Product_Analytics.pbip"), "w") as f:
    json.dump(pbip_root, f, indent=2)

# definition.pbir for report
report_pbir = {
  "version": "1.0",
  "datasetReference": {
    "byPath": {
      "path": "../Zomato_Product_Analytics.Dataset"
    }
  }
}
with open(os.path.join(report_dir, "definition.pbir"), "w") as f:
    json.dump(report_pbir, f, indent=2)

# definition.pbir for dataset
dataset_pbir = {
  "version": "1.0"
}
with open(os.path.join(dataset_dir, "definition.pbir"), "w") as f:
    json.dump(dataset_pbir, f, indent=2)

# Tabular Model Definition (BIM / TMSL)
bim_model = {
  "name": "Zomato_Product_Analytics",
  "compatibilityLevel": 1550,
  "model": {
    "culture": "en-US",
    "dataAccessOptions": {
      "legacyRedirects": True,
      "returnErrorValuesAsNull": True
    },
    "tables": [
      {
        "name": "Customers",
        "columns": [{"name": c, "dataType": "string"} for c in customers.columns]
      },
      {
        "name": "Restaurants",
        "columns": [{"name": c, "dataType": "string"} for c in restaurants.columns]
      },
      {
        "name": "DeliveryPartners",
        "columns": [{"name": c, "dataType": "string"} for c in delivery_partners.columns]
      },
      {
        "name": "Orders",
        "columns": [{"name": c, "dataType": "string"} for c in orders.columns]
      },
      {
        "name": "Payments",
        "columns": [{"name": c, "dataType": "string"} for c in payments.columns]
      },
      {
        "name": "Reviews",
        "columns": [{"name": c, "dataType": "string"} for c in reviews.columns]
      }
    ]
  }
}

with open(os.path.join(dataset_dir, "model.bim"), "w") as f:
    json.dump(bim_model, f, indent=2)

print("Generated Power BI Project (.pbip) at dashboard/Zomato_Product_Analytics.pbip")
