"""
================================================================================
Zomato Product Analytics Platform — Exploratory Data Analysis (EDA)
================================================================================
Author  : Zomato Analytics Team
Purpose : End-to-end EDA on all 6 datasets with chart exports to data/processed/
Run     : python python/eda.py  (from project root)
================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings

warnings.filterwarnings("ignore")

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RAW_DIR      = os.path.join(PROJECT_ROOT, "data", "raw")
OUT_DIR      = os.path.join(PROJECT_ROOT, "data", "processed")

os.makedirs(OUT_DIR, exist_ok=True)

# ── Styling ──────────────────────────────────────────────────────────────────
PALETTE   = ["#E23744", "#FF6B35", "#F7931E", "#FFC20E", "#4CAF50",
             "#2196F3", "#9C27B0", "#00BCD4"]
ZOMATO_RED = "#E23744"

plt.rcParams.update({
    "figure.facecolor": "#1a1a2e",
    "axes.facecolor":   "#16213e",
    "axes.edgecolor":   "#0f3460",
    "axes.labelcolor":  "#e0e0e0",
    "xtick.color":      "#e0e0e0",
    "ytick.color":      "#e0e0e0",
    "text.color":       "#e0e0e0",
    "grid.color":       "#0f3460",
    "grid.linewidth":   0.5,
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.titlepad":    12,
})

sns.set_theme(style="darkgrid", palette=PALETTE)


def save_fig(name: str, fig=None):
    """Save figure to data/processed/."""
    path = os.path.join(OUT_DIR, f"{name}.png")
    (fig or plt).savefig(path, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close("all")
    print(f"  [OK] Saved -> {name}.png")


# ============================================================
#  1. LOAD DATA
# ============================================================
def load_data():
    print("\n" + "="*60)
    print("  ZOMATO EDA — Loading Datasets")
    print("="*60)

    files = {
        "customers":        "customers.csv",
        "restaurants":      "restaurants.csv",
        "delivery_partners":"delivery_partners.csv",
        "orders":           "orders.csv",
        "payments":         "payments.csv",
        "reviews":          "reviews.csv",
    }

    dfs = {}
    for key, fname in files.items():
        path = os.path.join(RAW_DIR, fname)
        dfs[key] = pd.read_csv(path)
        print(f"  {fname:<30} ->  {dfs[key].shape[0]:>6,} rows  x  {dfs[key].shape[1]} cols")

    # Parse dates
    dfs["orders"]["order_date"] = pd.to_datetime(dfs["orders"]["order_date"])
    dfs["customers"]["signup_date"] = pd.to_datetime(dfs["customers"]["signup_date"])
    return dfs


# ============================================================
#  2. BASIC INFO / NULL REPORT
# ============================================================
def basic_info(dfs: dict):
    print("\n" + "="*60)
    print("  NULL VALUES REPORT")
    print("="*60)
    for name, df in dfs.items():
        nulls = df.isnull().sum().sum()
        print(f"  {name:<22}: {nulls} null values")

    print("\n" + "="*60)
    print("  DATA TYPES SUMMARY")
    print("="*60)
    for name, df in dfs.items():
        print(f"\n  [{name}]")
        for col, dtype in df.dtypes.items():
            print(f"    {col:<30} {str(dtype)}")


# ============================================================
#  3. CHART 1 — EXECUTIVE KPI CARDS
# ============================================================
def chart_kpi_summary(dfs: dict):
    print("\n[Chart 1] Executive KPI Summary")
    orders = dfs["orders"]
    delivered = orders[orders["status"] == "Delivered"]

    kpis = {
        "Total Orders":      f"{len(orders):,}",
        "Total Revenue":     f"₹{delivered['final_amount'].sum():,.0f}",
        "Avg Order Value":   f"₹{delivered['final_amount'].mean():,.1f}",
        "Avg Delivery Time": f"{orders['delivery_time_minutes'].mean():.1f} min",
        "Cancellation Rate": f"{(orders['status']=='Cancelled').mean()*100:.1f}%",
        "Unique Customers":  f"{orders['customer_id'].nunique():,}",
    }

    fig, axes = plt.subplots(2, 3, figsize=(16, 7))
    fig.suptitle("Zomato — Executive KPI Dashboard", fontsize=18, fontweight="bold",
                 color="#E23744", y=1.02)
    colors = ["#E23744", "#FF6B35", "#F7931E", "#FFC20E", "#4CAF50", "#2196F3"]

    for ax, (label, value), color in zip(axes.flatten(), kpis.items(), colors):
        ax.set_facecolor("#0f3460")
        ax.text(0.5, 0.62, value, ha="center", va="center", fontsize=26,
                fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.28, label, ha="center", va="center", fontsize=12,
                color="#b0b0b0", transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(color); spine.set_linewidth(2)

    plt.tight_layout()
    save_fig("01_executive_kpis", fig)


# ============================================================
#  4. CHART 2 — MONTHLY REVENUE TREND
# ============================================================
def chart_monthly_revenue(dfs: dict):
    print("[Chart 2] Monthly Revenue Trend")
    orders = dfs["orders"][dfs["orders"]["status"] == "Delivered"].copy()
    orders["month"] = orders["order_date"].dt.to_period("M")
    monthly = orders.groupby("month")["final_amount"].sum().reset_index()
    monthly["month_str"] = monthly["month"].astype(str)

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.fill_between(monthly["month_str"], monthly["final_amount"],
                    alpha=0.25, color=ZOMATO_RED)
    ax.plot(monthly["month_str"], monthly["final_amount"],
            color=ZOMATO_RED, linewidth=2.5, marker="o", markersize=6)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
    ax.set_title("Monthly Revenue Trend (Delivered Orders)")
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue")
    plt.xticks(rotation=45, ha="right")
    ax.grid(True, axis="y", alpha=0.4)
    plt.tight_layout()
    save_fig("02_monthly_revenue_trend", fig)


# ============================================================
#  5. CHART 3 — ORDER STATUS BREAKDOWN
# ============================================================
def chart_order_status(dfs: dict):
    print("[Chart 3] Order Status Breakdown")
    counts = dfs["orders"]["status"].value_counts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Order Status Analysis", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Pie chart
    wedge_colors = [ZOMATO_RED, "#FF6B35", "#FFC20E"]
    wedges, texts, autotexts = ax1.pie(
        counts.values, labels=counts.index, autopct="%1.1f%%",
        colors=wedge_colors, startangle=140,
        wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2)
    )
    for t in texts + autotexts:
        t.set_color("#e0e0e0"); t.set_fontsize(12)
    ax1.set_title("Status Distribution")

    # Bar chart
    bars = ax2.bar(counts.index, counts.values, color=wedge_colors, edgecolor="#1a1a2e", linewidth=1.5)
    for bar, val in zip(bars, counts.values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                 f"{val:,}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax2.set_title("Order Counts by Status")
    ax2.set_ylabel("Number of Orders")
    ax2.grid(True, axis="y", alpha=0.4)

    plt.tight_layout()
    save_fig("03_order_status_breakdown", fig)


# ============================================================
#  6. CHART 4 — REVENUE BY CITY
# ============================================================
def chart_revenue_by_city(dfs: dict):
    print("[Chart 4] Revenue by City")
    orders = dfs["orders"].merge(dfs["restaurants"][["restaurant_id", "city"]], on="restaurant_id")
    city_rev = (orders[orders["status"] == "Delivered"]
                .groupby("city")["final_amount"].sum()
                .sort_values(ascending=True))

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(city_rev.index, city_rev.values, color=PALETTE[:len(city_rev)],
                   edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, city_rev.values):
        ax.text(val + 20000, bar.get_y() + bar.get_height()/2,
                f"₹{val/1e5:.1f}L", va="center", fontsize=11, fontweight="bold")
    ax.set_title("Total Revenue by City")
    ax.set_xlabel("Revenue (₹)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.0f}L"))
    ax.grid(True, axis="x", alpha=0.4)
    plt.tight_layout()
    save_fig("04_revenue_by_city", fig)


# ============================================================
#  7. CHART 5 — TOP 10 RESTAURANTS BY REVENUE
# ============================================================
def chart_top_restaurants(dfs: dict):
    print("[Chart 5] Top 10 Restaurants by Revenue")
    merged = (dfs["orders"][dfs["orders"]["status"] == "Delivered"]
              .merge(dfs["restaurants"][["restaurant_id", "restaurant_name"]], on="restaurant_id"))
    top10 = (merged.groupby("restaurant_name")["final_amount"].sum()
             .sort_values(ascending=False).head(10))

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.barh(top10.index[::-1], top10.values[::-1],
                   color=[ZOMATO_RED] + [PALETTE[1]] * 9,
                   edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, top10.values[::-1]):
        ax.text(val + 5000, bar.get_y() + bar.get_height()/2,
                f"₹{val:,.0f}", va="center", fontsize=10)
    ax.set_title("Top 10 Restaurants by Revenue")
    ax.set_xlabel("Revenue (₹)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
    ax.grid(True, axis="x", alpha=0.4)
    plt.tight_layout()
    save_fig("05_top10_restaurants", fig)


# ============================================================
#  8. CHART 6 — CUISINE POPULARITY
# ============================================================
def chart_cuisine_popularity(dfs: dict):
    print("[Chart 6] Cuisine Popularity")
    merged = dfs["orders"].merge(dfs["restaurants"][["restaurant_id", "cuisine"]], on="restaurant_id")
    cuisine_orders = merged.groupby("cuisine")["order_id"].count().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(13, 6))
    bars = ax.bar(cuisine_orders.index, cuisine_orders.values, color=PALETTE,
                  edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, cuisine_orders.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                f"{val:,}", ha="center", va="bottom", fontsize=10)
    ax.set_title("Orders by Cuisine Type")
    ax.set_ylabel("Number of Orders")
    plt.xticks(rotation=30, ha="right")
    ax.grid(True, axis="y", alpha=0.4)
    plt.tight_layout()
    save_fig("06_cuisine_popularity", fig)


# ============================================================
#  9. CHART 7 — CUSTOMER AGE DISTRIBUTION
# ============================================================
def chart_customer_demographics(dfs: dict):
    print("[Chart 7] Customer Demographics")
    customers = dfs["customers"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Customer Demographics", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Age distribution
    axes[0].hist(customers["age"], bins=20, color=ZOMATO_RED, edgecolor="#1a1a2e", linewidth=0.8)
    axes[0].set_title("Age Distribution"); axes[0].set_xlabel("Age"); axes[0].set_ylabel("Count")
    axes[0].grid(True, axis="y", alpha=0.4)

    # Gender split
    gender_counts = customers["gender"].value_counts()
    axes[1].pie(gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%",
                colors=PALETTE[:3], startangle=90,
                wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2))
    axes[1].set_title("Gender Distribution")
    for t in axes[1].texts:
        t.set_color("#e0e0e0"); t.set_fontsize(11)

    # Zomato Gold
    gold_counts = customers["zomato_gold"].value_counts()
    gold_labels = {True: "Gold Member", False: "Regular", 1: "Gold Member", 0: "Regular"}
    labels = [gold_labels.get(k, str(k)) for k in gold_counts.index]
    axes[2].pie(gold_counts.values, labels=labels, autopct="%1.1f%%",
                colors=["#FFC20E", "#9E9E9E"], startangle=90,
                wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2))
    axes[2].set_title("Zomato Gold Membership")
    for t in axes[2].texts:
        t.set_color("#e0e0e0"); t.set_fontsize(11)

    plt.tight_layout()
    save_fig("07_customer_demographics", fig)


# ============================================================
# 10. CHART 8 — ORDER AMOUNT DISTRIBUTION
# ============================================================
def chart_order_amount_dist(dfs: dict):
    print("[Chart 8] Order Amount Distribution")
    orders = dfs["orders"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Order Value Analysis", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Histogram
    axes[0].hist(orders["final_amount"], bins=40, color=ZOMATO_RED,
                 edgecolor="#1a1a2e", linewidth=0.6, alpha=0.85)
    axes[0].axvline(orders["final_amount"].mean(), color="#FFC20E", linewidth=2,
                    linestyle="--", label=f"Mean: ₹{orders['final_amount'].mean():.0f}")
    axes[0].axvline(orders["final_amount"].median(), color="#4CAF50", linewidth=2,
                    linestyle="--", label=f"Median: ₹{orders['final_amount'].median():.0f}")
    axes[0].set_title("Final Amount Distribution")
    axes[0].set_xlabel("Order Amount (₹)"); axes[0].set_ylabel("Frequency")
    axes[0].legend(facecolor="#16213e", edgecolor="#0f3460")
    axes[0].grid(True, axis="y", alpha=0.4)

    # Box plot by status
    status_data = [orders[orders["status"] == s]["final_amount"].values
                   for s in ["Delivered", "Cancelled", "Delayed"]]
    bp = axes[1].boxplot(status_data, tick_labels=["Delivered", "Cancelled", "Delayed"],
                         patch_artist=True, notch=False)
    for patch, color in zip(bp["boxes"], [PALETTE[0], PALETTE[1], PALETTE[2]]):
        patch.set_facecolor(color); patch.set_alpha(0.75)
    for element in ["whiskers", "caps", "medians", "fliers"]:
        for item in bp[element]:
            item.set_color("#e0e0e0")
    axes[1].set_title("Order Amount by Status")
    axes[1].set_ylabel("Amount (₹)")
    axes[1].grid(True, axis="y", alpha=0.4)

    plt.tight_layout()
    save_fig("08_order_amount_distribution", fig)


# ============================================================
# 11. CHART 9 — PAYMENT METHOD ANALYSIS
# ============================================================
def chart_payment_analysis(dfs: dict):
    print("[Chart 9] Payment Method Analysis")
    payments = dfs["payments"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Payment Analytics", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Payment method distribution
    method_counts = payments["payment_method"].value_counts()
    bars = axes[0].bar(method_counts.index, method_counts.values, color=PALETTE,
                       edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, method_counts.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                     f"{val:,}", ha="center", fontsize=10, fontweight="bold")
    axes[0].set_title("Payment Method Usage")
    axes[0].set_ylabel("Transactions"); axes[0].set_xlabel("Payment Method")
    axes[0].grid(True, axis="y", alpha=0.4)

    # Payment status
    status_counts = payments["payment_status"].value_counts()
    wedges, texts, autotexts = axes[1].pie(
        status_counts.values, labels=status_counts.index, autopct="%1.1f%%",
        colors=["#4CAF50", ZOMATO_RED, "#FF6B35"],
        startangle=140, wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2)
    )
    for t in texts + autotexts:
        t.set_color("#e0e0e0"); t.set_fontsize(11)
    axes[1].set_title("Payment Status Breakdown")

    plt.tight_layout()
    save_fig("09_payment_analysis", fig)


# ============================================================
# 12. CHART 10 — DELIVERY PARTNER PERFORMANCE
# ============================================================
def chart_delivery_partners(dfs: dict):
    print("[Chart 10] Delivery Partner Performance")
    orders = dfs["orders"]
    partners = dfs["delivery_partners"]

    merged = orders.merge(partners[["partner_id", "vehicle_type", "rating"]], on="partner_id")

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Delivery Partner Performance", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Avg delivery time by vehicle type
    vehicle_perf = merged.groupby("vehicle_type")["delivery_time_minutes"].mean().sort_values()
    bars = axes[0].barh(vehicle_perf.index, vehicle_perf.values, color=PALETTE[:3],
                        edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, vehicle_perf.values):
        axes[0].text(val + 0.2, bar.get_y() + bar.get_height()/2,
                     f"{val:.1f} min", va="center", fontsize=11)
    axes[0].set_title("Avg Delivery Time by Vehicle Type")
    axes[0].set_xlabel("Minutes"); axes[0].grid(True, axis="x", alpha=0.4)

    # Partner rating distribution
    axes[1].hist(partners["rating"], bins=15, color="#2196F3", edgecolor="#1a1a2e", linewidth=0.8)
    axes[1].axvline(partners["rating"].mean(), color=ZOMATO_RED, linewidth=2, linestyle="--",
                    label=f"Mean: {partners['rating'].mean():.2f}")
    axes[1].set_title("Delivery Partner Rating Distribution")
    axes[1].set_xlabel("Rating"); axes[1].set_ylabel("Count")
    axes[1].legend(facecolor="#16213e", edgecolor="#0f3460")
    axes[1].grid(True, axis="y", alpha=0.4)

    plt.tight_layout()
    save_fig("10_delivery_partner_performance", fig)


# ============================================================
# 13. CHART 11 — CANCELLATION ANALYSIS
# ============================================================
def chart_cancellation_analysis(dfs: dict):
    print("[Chart 11] Cancellation Rate Analysis")
    orders = dfs["orders"]
    restaurants = dfs["restaurants"]
    merged = orders.merge(restaurants[["restaurant_id", "city", "cuisine"]], on="restaurant_id")

    # Cancellation rate by city
    cancel_city = (merged.groupby("city")
                   .apply(lambda x: (x["status"] == "Cancelled").mean() * 100)
                   .sort_values(ascending=False)
                   .reset_index(name="cancel_rate"))

    # Cancellation rate by cuisine
    cancel_cuisine = (merged.groupby("cuisine")
                      .apply(lambda x: (x["status"] == "Cancelled").mean() * 100)
                      .sort_values(ascending=False)
                      .reset_index(name="cancel_rate"))

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Cancellation Rate Analysis", fontsize=16, fontweight="bold", color="#e0e0e0")

    # By city
    bars1 = axes[0].bar(cancel_city["city"], cancel_city["cancel_rate"],
                        color=PALETTE[:len(cancel_city)], edgecolor="#1a1a2e")
    for bar, val in zip(bars1, cancel_city["cancel_rate"]):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                     f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")
    axes[0].set_title("Cancellation Rate by City")
    axes[0].set_ylabel("Cancellation Rate (%)")
    plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=30, ha="right")
    axes[0].grid(True, axis="y", alpha=0.4)

    # By cuisine
    bars2 = axes[1].barh(cancel_cuisine["cuisine"][::-1], cancel_cuisine["cancel_rate"][::-1],
                         color=PALETTE[:len(cancel_cuisine)], edgecolor="#1a1a2e")
    for bar, val in zip(bars2, cancel_cuisine["cancel_rate"][::-1]):
        axes[1].text(val + 0.05, bar.get_y() + bar.get_height()/2,
                     f"{val:.1f}%", va="center", fontsize=10)
    axes[1].set_title("Cancellation Rate by Cuisine")
    axes[1].set_xlabel("Cancellation Rate (%)")
    axes[1].grid(True, axis="x", alpha=0.4)

    plt.tight_layout()
    save_fig("11_cancellation_analysis", fig)


# ============================================================
# 14. CHART 12 — HOURLY ORDER PATTERN (HEATMAP)
# ============================================================
def chart_hourly_heatmap(dfs: dict):
    print("[Chart 12] Hourly Order Heatmap")
    orders = dfs["orders"].copy()
    orders["hour"] = pd.to_datetime(orders["order_time"], format="%H:%M:%S").dt.hour
    orders["day_of_week"] = orders["order_date"].dt.day_name()

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = (orders.groupby(["day_of_week", "hour"])["order_id"]
             .count().unstack(fill_value=0)
             .reindex(day_order, fill_value=0))

    fig, ax = plt.subplots(figsize=(18, 6))
    sns.heatmap(pivot, cmap="YlOrRd", ax=ax, linewidths=0.3,
                cbar_kws={"label": "Number of Orders"}, annot=False)
    ax.set_title("Order Volume Heatmap — Day vs Hour")
    ax.set_xlabel("Hour of Day"); ax.set_ylabel("Day of Week")
    plt.tight_layout()
    save_fig("12_hourly_order_heatmap", fig)


# ============================================================
# 15. CHART 13 — GOLD vs NON-GOLD MEMBER ANALYSIS
# ============================================================
def chart_gold_members(dfs: dict):
    print("[Chart 13] Gold vs Non-Gold Member Analysis")
    orders = dfs["orders"]
    customers = dfs["customers"][["customer_id", "zomato_gold"]]
    merged = orders.merge(customers, on="customer_id")
    merged["member_type"] = merged["zomato_gold"].map({True: "Gold", False: "Regular",
                                                        1: "Gold", 0: "Regular"})

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Zomato Gold vs Regular Member Analysis", fontsize=16,
                 fontweight="bold", color="#e0e0e0")

    # Avg order value
    avg_val = merged.groupby("member_type")["final_amount"].mean()
    bars = axes[0].bar(avg_val.index, avg_val.values, color=["#FFC20E", "#9E9E9E"],
                       edgecolor="#1a1a2e", linewidth=1.5, width=0.4)
    for bar, val in zip(bars, avg_val.values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                     f"₹{val:.0f}", ha="center", fontsize=13, fontweight="bold")
    axes[0].set_title("Avg Order Value"); axes[0].set_ylabel("₹")
    axes[0].grid(True, axis="y", alpha=0.4)

    # Total revenue share
    rev_share = merged.groupby("member_type")["final_amount"].sum()
    axes[1].pie(rev_share.values, labels=rev_share.index, autopct="%1.1f%%",
                colors=["#FFC20E", "#9E9E9E"],
                wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2))
    axes[1].set_title("Revenue Share")
    for t in axes[1].texts:
        t.set_color("#e0e0e0"); t.set_fontsize(12)

    # Orders per member
    orders_per = merged.groupby("member_type")["order_id"].count()
    bars2 = axes[2].bar(orders_per.index, orders_per.values, color=["#FFC20E", "#9E9E9E"],
                        edgecolor="#1a1a2e", linewidth=1.5, width=0.4)
    for bar, val in zip(bars2, orders_per.values):
        axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                     f"{val:,}", ha="center", fontsize=13, fontweight="bold")
    axes[2].set_title("Total Orders Placed"); axes[2].set_ylabel("Orders")
    axes[2].grid(True, axis="y", alpha=0.4)

    plt.tight_layout()
    save_fig("13_gold_vs_regular_members", fig)


# ============================================================
# 16. CHART 14 — RESTAURANT RATING DISTRIBUTION
# ============================================================
def chart_restaurant_ratings(dfs: dict):
    print("[Chart 14] Restaurant & Review Ratings")
    restaurants = dfs["restaurants"]
    reviews = dfs["reviews"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Rating Analysis", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Restaurant avg rating
    axes[0].hist(restaurants["average_rating"], bins=15, color="#FF6B35",
                 edgecolor="#1a1a2e", linewidth=0.8)
    axes[0].axvline(restaurants["average_rating"].mean(), color="#FFC20E",
                    linewidth=2, linestyle="--",
                    label=f"Mean: {restaurants['average_rating'].mean():.2f}")
    axes[0].set_title("Restaurant Average Rating Distribution")
    axes[0].set_xlabel("Rating"); axes[0].set_ylabel("Restaurants")
    axes[0].legend(facecolor="#16213e")
    axes[0].grid(True, axis="y", alpha=0.4)

    # Customer review ratings
    review_counts = reviews["rating"].value_counts().sort_index()
    bars = axes[1].bar(review_counts.index, review_counts.values,
                       color=PALETTE[:5], edgecolor="#1a1a2e", linewidth=1)
    for bar, val in zip(bars, review_counts.values):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                     f"{val:,}", ha="center", fontsize=11, fontweight="bold")
    axes[1].set_title("Customer Review Ratings (1–5 Stars)")
    axes[1].set_xlabel("Rating (Stars)"); axes[1].set_ylabel("Count")
    axes[1].set_xticks([1, 2, 3, 4, 5])
    axes[1].grid(True, axis="y", alpha=0.4)

    plt.tight_layout()
    save_fig("14_rating_analysis", fig)


# ============================================================
# 17. CHART 15 — DELIVERY TIME DISTRIBUTION
# ============================================================
def chart_delivery_time(dfs: dict):
    print("[Chart 15] Delivery Time Analysis")
    orders = dfs["orders"]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Delivery Time Analysis", fontsize=16, fontweight="bold", color="#e0e0e0")

    # Overall distribution
    axes[0].hist(orders["delivery_time_minutes"], bins=30, color="#2196F3",
                 edgecolor="#1a1a2e", linewidth=0.7, alpha=0.85)
    axes[0].axvline(orders["delivery_time_minutes"].mean(), color=ZOMATO_RED,
                    linewidth=2, linestyle="--",
                    label=f"Mean: {orders['delivery_time_minutes'].mean():.1f} min")
    axes[0].axvline(30, color="#4CAF50", linewidth=2, linestyle=":",
                    label="30-min SLA Target")
    axes[0].set_title("Delivery Time Distribution")
    axes[0].set_xlabel("Minutes"); axes[0].set_ylabel("Orders")
    axes[0].legend(facecolor="#16213e")
    axes[0].grid(True, axis="y", alpha=0.4)

    # SLA Breach Analysis (>30 min = breach)
    orders["sla_breach"] = orders["delivery_time_minutes"] > 30
    breach_counts = orders["sla_breach"].value_counts()
    labels = ["On Time (≤30 min)", "SLA Breach (>30 min)"]
    wedges, texts, autotexts = axes[1].pie(
        breach_counts.values, labels=labels, autopct="%1.1f%%",
        colors=["#4CAF50", ZOMATO_RED],
        startangle=90, wedgeprops=dict(edgecolor="#1a1a2e", linewidth=2)
    )
    for t in texts + autotexts:
        t.set_color("#e0e0e0"); t.set_fontsize(12)
    axes[1].set_title("SLA Breach Analysis (30-min Target)")

    plt.tight_layout()
    save_fig("15_delivery_time_analysis", fig)


# ============================================================
# 18. PRINT SUMMARY STATISTICS
# ============================================================
def print_summary(dfs: dict):
    print("\n" + "="*60)
    print("  FINAL SUMMARY STATISTICS")
    print("="*60)
    orders = dfs["orders"]
    delivered = orders[orders["status"] == "Delivered"]

    print(f"  Total Orders        : {len(orders):,}")
    print(f"  Total Revenue       : ₹{delivered['final_amount'].sum():,.2f}")
    print(f"  Avg Order Value     : ₹{delivered['final_amount'].mean():,.2f}")
    print(f"  Cancellation Rate   : {(orders['status']=='Cancelled').mean()*100:.2f}%")
    print(f"  Delay Rate          : {(orders['status']=='Delayed').mean()*100:.2f}%")
    print(f"  Avg Delivery Time   : {orders['delivery_time_minutes'].mean():.1f} min")
    print(f"  SLA Breach (>30min) : {(orders['delivery_time_minutes'] > 30).mean()*100:.2f}%")
    print(f"  Unique Customers    : {orders['customer_id'].nunique():,}")
    print(f"  Unique Restaurants  : {orders['restaurant_id'].nunique():,}")
    print(f"  Total Reviews       : {len(dfs['reviews']):,}")
    print(f"  Avg Review Rating   : {dfs['reviews']['rating'].mean():.2f} / 5.0")


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "="*60)
    print("  ZOMATO PRODUCT ANALYTICS PLATFORM - EDA")
    print("="*60)

    dfs = load_data()
    basic_info(dfs)

    print("\n" + "="*60)
    print("  GENERATING CHARTS  ->  data/processed/")
    print("="*60)

    chart_kpi_summary(dfs)
    chart_monthly_revenue(dfs)
    chart_order_status(dfs)
    chart_revenue_by_city(dfs)
    chart_top_restaurants(dfs)
    chart_cuisine_popularity(dfs)
    chart_customer_demographics(dfs)
    chart_order_amount_dist(dfs)
    chart_payment_analysis(dfs)
    chart_delivery_partners(dfs)
    chart_cancellation_analysis(dfs)
    chart_hourly_heatmap(dfs)
    chart_gold_members(dfs)
    chart_restaurant_ratings(dfs)
    chart_delivery_time(dfs)

    print_summary(dfs)

    print("\n" + "="*60)
    print("  [DONE] EDA COMPLETE - 15 Charts saved to data/processed/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
