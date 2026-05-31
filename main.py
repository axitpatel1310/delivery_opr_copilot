import pandas as pd
import json
# ==========================
# LOAD DATA
# ==========================

restaurants = pd.read_csv("https://huggingface.co/datasets/akkypatel705/delivery-operations-dataset/resolve/main/restaurants.csv")
couriers = pd.read_csv("https://huggingface.co/datasets/akkypatel705/delivery-operations-dataset/resolve/main/couriers.csv")
orders = pd.read_csv("https://huggingface.co/datasets/akkypatel705/delivery-operations-dataset/resolve/main/orders.csv")
events = pd.read_csv("https://huggingface.co/datasets/akkypatel705/delivery-operations-dataset/resolve/main/order_events.csv")
incidents = pd.read_csv("https://huggingface.co/datasets/akkypatel705/delivery-operations-dataset/resolve/main/incidents.csv")

# ==========================
# PREPARE TIMESTAMPS
# ==========================

orders["created_at"] = pd.to_datetime(
    orders["created_at"]
)

events["timestamp"] = pd.to_datetime(
    events["timestamp"]
)

# ==========================
# BUILD ORDER LIFECYCLE
# ==========================

lifecycle = (
    events.pivot_table(
        index="order_id",
        columns="event_type",
        values="timestamp",
        aggfunc="first"
    )
    .reset_index()
)

# Flatten column names
lifecycle.columns.name = None

# ==========================
# CREATE METRICS
# ==========================

lifecycle["prep_time"] = (
    lifecycle["ORDER_READY"]
    - lifecycle["ORDER_CREATED"]
).dt.total_seconds() / 60

lifecycle["assignment_time"] = (
    lifecycle["COURIER_ASSIGNED"]
    - lifecycle["ORDER_CREATED"]
).dt.total_seconds() / 60

lifecycle["travel_time"] = (
    lifecycle["ORDER_DELIVERED"]
    - lifecycle["ORDER_PICKED_UP"]
).dt.total_seconds() / 60

lifecycle["delivery_time"] = (
    lifecycle["ORDER_DELIVERED"]
    - lifecycle["ORDER_CREATED"]
).dt.total_seconds() / 60

# ==========================
# JOIN ORDERS
# ==========================

order_metrics = orders.merge(
    lifecycle[
        [
            "order_id",
            "prep_time",
            "assignment_time",
            "travel_time",
            "delivery_time",
        ]
    ],
    on="order_id",
    how="inner",
)

# ==========================
# GLOBAL KPIs
# ==========================

total_orders = len(order_metrics)

total_revenue = (
    order_metrics["order_value_eur"]
    .sum()
)

avg_delivery_time = (
    order_metrics["delivery_time"]
    .mean()
)

avg_prep_time = (
    order_metrics["prep_time"]
    .mean()
)

avg_assignment_time = (
    order_metrics["assignment_time"]
    .mean()
)

avg_travel_time = (
    order_metrics["travel_time"]
    .mean()
)

LATE_THRESHOLD = 40

late_rate = (
    (
        order_metrics["delivery_time"]
        > LATE_THRESHOLD
    )
    .mean()
    * 100
)
# ==========================
# RESTAURANT ANALYTICS
# ==========================

restaurant_perf = (
    order_metrics
    .groupby("restaurant_id")
    .agg(
        avg_prep_time=("prep_time", "mean"),
        orders=("order_id", "count"),
    )
    .reset_index()
)

restaurant_perf = restaurant_perf.merge(
    restaurants[
        ["restaurant_id", "restaurant_name"]
    ],
    on="restaurant_id",
)

slow_restaurants = (
    restaurant_perf
    .sort_values(
        "avg_prep_time",
        ascending=False
    )
    .head(5)
)

# ==========================
# ZONE ANALYTICS
# ==========================

zone_perf = (
    order_metrics
    .groupby("zone")
    .agg(
        avg_delivery_time=(
            "delivery_time",
            "mean"
        ),
        revenue=(
            "order_value_eur",
            "sum"
        ),
        orders=(
            "order_id",
            "count"
        ),
    )
    .reset_index()
)

slow_zones = (
    zone_perf
    .sort_values(
        "avg_delivery_time",
        ascending=False
    )
    .head(5)
)

# ==========================
# ROOT CAUSE ANALYSIS
# ==========================

if (
    avg_assignment_time
    > avg_prep_time
    and avg_assignment_time
    > avg_travel_time
):
    cause = "Courier Shortage"

    recommendation = (
        "Increase rider supply "
        "during peak demand."
    )

elif (
    avg_prep_time
    > avg_assignment_time
    and avg_prep_time
    > avg_travel_time
):
    cause = "Restaurant Delays"

    recommendation = (
        "Investigate restaurants "
        "with long preparation times."
    )

else:
    cause = "Traffic / Travel Delays"

    recommendation = (
        "Optimize delivery routing "
        "and courier allocation."
    )

# ==========================
# EXECUTIVE REPORT
# ==========================

print("\n" + "=" * 60)
print("DELIVERY OPERATIONS COPILOT")
print("=" * 60)

print(f"\nOrders: {total_orders:,}")
print(f"Revenue: €{total_revenue:,.2f}")
print(
    f"Average Delivery Time: "
    f"{avg_delivery_time:.2f} min"
)
print(
    f"Late Deliveries: "
    f"{late_rate:.2f}%"
)

print("\n" + "-" * 60)
print("TOP DELAYED ZONES")
print("-" * 60)

for _, row in slow_zones.iterrows():
    print(
        f"{row['zone']:<20}"
        f"{row['avg_delivery_time']:.2f} min"
    )

print("\n" + "-" * 60)
print("TOP SLOW RESTAURANTS")
print("-" * 60)

for _, row in slow_restaurants.iterrows():
    print(
        f"{row['restaurant_name']:<30}"
        f"{row['avg_prep_time']:.2f} min"
    )

print("\n" + "-" * 60)
print("ROOT CAUSE ANALYSIS")
print("-" * 60)

print(f"Primary Cause: {cause}")

print(
    f"\nAverage Prep Time: "
    f"{avg_prep_time:.2f} min"
)

print(
    f"Average Assignment Time: "
    f"{avg_assignment_time:.2f} min"
)

print(
    f"Average Travel Time: "
    f"{avg_travel_time:.2f} min"
)

print(
    f"\nRecommendation: "
    f"{recommendation}"
)

print("\n" + "=" * 60)

report = {
    "kpis": {
        "orders": total_orders,
        "revenue": float(total_revenue),
        "avgDelivery": round(
            avg_delivery_time, 2
        ),
        "lateRate": round(
            late_rate, 2
        ),
    },

    "rootCause": {
        "cause": cause,
        "recommendation": recommendation,
    }
}
with open(
    "frontend/public/report.json",
    "w"
) as f:
    json.dump(
        report,
        f,
        indent=2
    )