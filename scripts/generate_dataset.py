import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def generate(rows: int, out_path: str):
    rng = np.random.default_rng(42)
    dates = pd.date_range('2023-01-01', periods=730, freq='D')
    stores = [f'ST{str(i).zfill(3)}' for i in range(1, 101)]
    products = [f'PR{str(i).zfill(4)}' for i in range(1, 501)]
    categories = ['Grocery', 'Electronics', 'Fashion', 'Home', 'Beauty', 'Sports']
    regions = ['North', 'South', 'East', 'West', 'Central']

    df = pd.DataFrame({
        'date': rng.choice(dates, rows),
        'store_id': rng.choice(stores, rows),
        'product_id': rng.choice(products, rows),
        'category': rng.choice(categories, rows, p=[.35,.12,.18,.15,.12,.08]),
        'region': rng.choice(regions, rows),
    })
    df['date'] = pd.to_datetime(df['date'])
    day = df['date'].dt.dayofweek
    month = df['date'].dt.month

    base_price = {'Grocery': 180, 'Electronics': 1500, 'Fashion': 800, 'Home': 650, 'Beauty': 350, 'Sports': 900}
    df['price'] = df['category'].map(base_price).astype(float) * rng.normal(1, .18, rows)
    df['discount_pct'] = np.clip(rng.normal(.10, .08, rows), 0, .45)
    df['competitor_price'] = df['price'] * rng.normal(1.02, .12, rows)
    df['inventory'] = rng.integers(5, 500, rows)
    df['weather_temp'] = 25 + 8*np.sin(2*np.pi*month/12) + rng.normal(0, 3, rows)
    df['rainfall_mm'] = np.where(month.isin([6,7,8,9]), rng.gamma(2, 8, rows), rng.gamma(1, 2, rows))
    df['holiday_flag'] = ((month == 10) | (month == 11) | ((month == 12) & (df['date'].dt.day > 20))).astype(int)
    df['event_flag'] = rng.binomial(1, .06, rows)

    category_base = df['category'].map({'Grocery': 70, 'Electronics': 12, 'Fashion': 30, 'Home': 24, 'Beauty': 34, 'Sports': 20}).astype(float)
    weekend = np.where(day >= 5, 1.18, 1.0)
    discount_boost = 1 + df['discount_pct'] * 2.5
    holiday_boost = 1 + df['holiday_flag'] * .45
    event_boost = 1 + df['event_flag'] * .30
    price_penalty = np.clip(1.15 - (df['price'] / df['competitor_price']) * .15, .75, 1.25)
    rain_penalty = np.where(df['rainfall_mm'] > 25, .88, 1.0)
    noise = rng.normal(1, .18, rows)
    demand = category_base * weekend * discount_boost * holiday_boost * event_boost * price_penalty * rain_penalty * noise
    demand = np.minimum(demand, df['inventory'] + rng.integers(0, 40, rows))
    df['units_sold'] = np.clip(np.round(demand), 0, None).astype(int)
    df['revenue'] = (df['units_sold'] * df['price'] * (1 - df['discount_pct'])).round(2)

    df = df.sort_values(['date', 'store_id', 'product_id']).reset_index(drop=True)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f'Saved {len(df):,} rows to {out_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=500_000)
    parser.add_argument('--out', default='data/raw/retail_demand.csv')
    args = parser.parse_args()
    generate(args.rows, args.out)
