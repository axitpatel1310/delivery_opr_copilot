import pandas as pd
import numpy as np
import datetime

np.random.seed(42)

ZONES = [f'zone_{i}' for i in range(1, 11)]
CUISINES = ['Italian', 'Chinese', 'Indian', 'Mexican', 'Burger', 'Sushi', 'Pizza', 'Vegan', 'Middle_Eastern', 'American']
START_DATE = datetime.datetime(2025, 1, 1)
HOURS_IN_YEAR = 8760
NUM_ORDERS = 1_000_000

# 1. Restaurants
rest_zones = np.random.choice(ZONES, 100)
rest_cuisines = np.random.choice(CUISINES, 100)
prep_times = np.clip(np.random.normal(16, 5, 100), 8, 32).astype(int)
df_restaurants = pd.DataFrame({
    'restaurant_id': [f'R{i:04d}' for i in range(1, 101)],
    'restaurant_name': [f'{c}_Kitchen_{i+1}' for i, c in enumerate(rest_cuisines)],
    'zone': rest_zones,
    'cuisine_type': rest_cuisines,
    'avg_prep_time_minutes': prep_times
})
df_restaurants.to_csv('restaurants.csv', index=False)

# 2. Couriers
df_couriers = pd.DataFrame({
    'courier_id': [f'C{i:04d}' for i in range(1, 501)],
    'home_zone': np.random.choice(ZONES, 500, p=[0.18, 0.16, 0.15, 0.12, 0.1, 0.08, 0.07, 0.05, 0.05, 0.04]),
    'speed_multiplier': np.round(np.random.uniform(0.75, 1.35, 500), 2),
    'vehicle_type': np.random.choice(['bicycle', 'e_bike', 'scooter', 'car'], 500, p=[0.4, 0.35, 0.15, 0.1])
})
df_couriers.to_csv('couriers.csv', index=False)

# 3. Orders
hour_weights = np.array([2, 1, 0.8, 0.7, 0.9, 2, 4, 7, 10, 12, 14, 16, 15, 12, 9, 8, 10, 15, 19, 22, 18, 12, 8, 4])
dow_weights = np.array([1.0, 1.0, 1.0, 1.05, 1.4, 1.6, 1.3])
month_weights = np.array([0.85, 0.9, 0.95, 1.0, 1.05, 1.15, 1.1, 1.05, 0.95, 1.0, 1.15, 1.2])

hours_rng = pd.date_range(start=START_DATE, periods=HOURS_IN_YEAR, freq='h')
probs = (hour_weights[hours_rng.hour.values] *
         dow_weights[hours_rng.dayofweek.values] *
         month_weights[hours_rng.month.values - 1])
probs /= probs.sum()

sampled_indices = np.random.choice(HOURS_IN_YEAR, size=NUM_ORDERS, p=probs)
base_ts = hours_rng[sampled_indices].values
base_ts += np.random.randint(0, 60, NUM_ORDERS) * np.timedelta64(1, 'm')
base_ts += np.random.randint(0, 60, NUM_ORDERS) * np.timedelta64(1, 's')
base_ts.sort()

rest_ids = df_restaurants['restaurant_id'].values
chosen_rest_idx = np.random.randint(0, 100, NUM_ORDERS)
chosen_rest_ids = rest_ids[chosen_rest_idx]
zones_map = dict(zip(df_restaurants['restaurant_id'], df_restaurants['zone']))
prep_map = dict(zip(df_restaurants['restaurant_id'], df_restaurants['avg_prep_time_minutes']))
order_zones = np.array([zones_map[r] for r in chosen_rest_ids])
order_preps = np.array([prep_map[r] for r in chosen_rest_ids])

df_orders = pd.DataFrame({
    'order_id': [f'O{i:07d}' for i in range(1, NUM_ORDERS+1)],
    'customer_id': [f'cust_{i:06d}' for i in np.random.randint(1, 80001, NUM_ORDERS)],
    'restaurant_id': chosen_rest_ids,
    'zone': order_zones,
    'order_value_eur': np.round(np.random.uniform(10, 60, NUM_ORDERS), 2),
    'created_at': pd.to_datetime(base_ts),
    'status': np.random.choice(['DELIVERED', 'CANCELLED', 'FAILED', 'IN_PROGRESS'], NUM_ORDERS, p=[0.85, 0.08, 0.04, 0.03])
})
df_orders.to_csv('orders.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')

# 4. Order Events
courier_speeds = np.random.uniform(0.75, 1.35, NUM_ORDERS)
t0 = df_orders['created_at'].values.astype('datetime64[s]')
d_accept = np.random.uniform(60, 180, NUM_ORDERS)
d_assign = d_accept + np.random.uniform(90, 240, NUM_ORDERS)
d_ready = d_assign + (order_preps * 60 * np.random.uniform(0.8, 1.2, NUM_ORDERS))
d_pickup = d_ready + np.random.uniform(120, 300, NUM_ORDERS)
d_deliver = d_pickup + (1500 * np.random.uniform(1.0, 1.6, NUM_ORDERS) / courier_speeds)

d_assign = np.maximum(d_assign, d_accept + 30)
d_ready = np.maximum(d_ready, d_assign + 60)
d_pickup = np.maximum(d_pickup, d_ready + 60)
d_deliver = np.maximum(d_deliver, d_pickup + 300)

t1 = t0 + d_accept.astype('timedelta64[s]')
t2 = t0 + d_assign.astype('timedelta64[s]')
t3 = t0 + d_ready.astype('timedelta64[s]')
t4 = t0 + d_pickup.astype('timedelta64[s]')
t5 = t0 + d_deliver.astype('timedelta64[s]')

events_order_ids = np.repeat(df_orders['order_id'].values, 6)
events_types = np.tile(['ORDER_CREATED', 'ORDER_ACCEPTED', 'COURIER_ASSIGNED', 'ORDER_READY', 'ORDER_PICKED_UP', 'ORDER_DELIVERED'], NUM_ORDERS)
events_times = np.concatenate([t0, t1, t2, t3, t4, t5])

df_events = pd.DataFrame({
    'event_id': [f'E{i:08d}' for i in range(1, len(events_times)+1)],
    'order_id': events_order_ids,
    'event_type': events_types,
    'timestamp': events_times
})
df_events = df_events.sort_values(['order_id', 'timestamp']).reset_index(drop=True)
df_events['event_id'] = [f'E{i:08d}' for i in range(1, len(df_events)+1)]
df_events.to_csv('order_events.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')

# 5. Incidents
inc_types = ['COURIER_SHORTAGE', 'DEMAND_SURGE', 'RESTAURANT_OUTAGE', 'TRAFFIC_CONGESTION', 'WEATHER_EVENT']
num_inc = 200
inc_df = pd.DataFrame({
    'incident_id': [f'I{i:05d}' for i in range(1, num_inc+1)],
    'incident_type': np.random.choice(inc_types, num_inc),
    'zone': np.random.choice(ZONES, num_inc),
    'severity': np.random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], num_inc, p=[0.3, 0.4, 0.2, 0.1]),
    'start_time': START_DATE + pd.to_timedelta(np.random.randint(0, HOURS_IN_YEAR, num_inc), unit='h')
})
dur_dict = {'COURIER_SHORTAGE': 8, 'DEMAND_SURGE': 5, 'RESTAURANT_OUTAGE': 24, 'TRAFFIC_CONGESTION': 7, 'WEATHER_EVENT': 14}
inc_df['end_time'] = inc_df.apply(lambda r: r['start_time'] + pd.to_timedelta(dur_dict[r['incident_type']] * np.random.uniform(0.5, 3.0), unit='h'), axis=1)
inc_df = inc_df.sort_values('start_time').reset_index(drop=True)
inc_df.to_csv('incidents.csv', index=False, date_format='%Y-%m-%d %H:%M:%S')

import pandas as pd
import numpy as np
import datetime

np.random.seed(42)

ZONES = [f'zone_{i}' for i in range(1, 11)]
START_DATE = datetime.datetime(2025, 1, 1)
END_DATE = datetime.datetime(2025, 12, 31, 23, 45)

timestamps = pd.date_range(start=START_DATE, end=END_DATE, freq='15min')
records = []

for zone in ZONES:
    zone_idx = ZONES.index(zone)
    base_couriers = np.random.randint(25, 60)
    base_demand = np.random.randint(40, 120)
    
    for ts in timestamps:
        hour = ts.hour
        dow = ts.dayofweek
        month = ts.month
        
        hour_factor = np.array([0.3, 0.2, 0.15, 0.1, 0.15, 0.4, 0.8, 1.3, 1.8, 2.0, 2.2, 2.4, 2.3, 2.0, 1.6, 1.4, 1.7, 2.3, 2.8, 3.2, 2.6, 1.8, 1.2, 0.6])[hour]
        dow_factor = np.array([1.0, 1.0, 1.0, 1.05, 1.4, 1.6, 1.3])[dow]
        month_factor = np.array([0.85, 0.9, 0.95, 1.0, 1.05, 1.15, 1.1, 1.05, 0.95, 1.0, 1.15, 1.2])[month-1]
        zone_factor = 1.0 + (zone_idx - 4.5) * 0.08
        
        active_couriers = int(base_couriers * hour_factor * dow_factor * zone_factor * np.random.uniform(0.9, 1.1))
        active_couriers = max(5, min(150, active_couriers))
        
        active_orders = int(base_demand * hour_factor * dow_factor * month_factor * zone_factor * np.random.uniform(0.85, 1.15))
        active_orders = max(0, min(300, active_orders))
        
        base_temp = 10 + 12 * np.sin((month - 4) * np.pi / 6)
        daily_variation = 5 * np.sin((hour - 6) * np.pi / 12)
        temperature_c = round(base_temp + daily_variation + np.random.normal(0, 2), 1)
        
        rain_prob = 0.15 + 0.1 * (month in [10, 11, 12, 1, 2])
        if np.random.random() < rain_prob:
            rain_intensity = round(np.random.exponential(0.4), 2)
            rain_intensity = min(1.0, rain_intensity)
        else:
            rain_intensity = 0.0
        
        records.append({
            'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'zone': zone,
            'active_couriers': active_couriers,
            'active_orders': active_orders,
            'temperature_c': temperature_c,
            'rain_intensity': rain_intensity
        })

df_zone_metrics = pd.DataFrame(records)
df_zone_metrics.to_csv('zone_metrics.csv', index=False)