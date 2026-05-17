from pathlib import Path
import pandas as pd

RAW = Path('data/raw/retail_demand.csv')
OUT = Path('data/processed/feature_store.csv')

def pandas_etl():
    df = pd.read_csv(RAW, parse_dates=['date'])
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['price_gap'] = df['competitor_price'] - df['price']
    df['sell_through_rate'] = df['units_sold'] / (df['inventory'] + 1)

    keys = ['store_id', 'product_id']
    df = df.sort_values(keys + ['date'])
    for lag in [1, 7, 14, 28]:
        df[f'lag_{lag}'] = df.groupby(keys)['units_sold'].shift(lag)
    for window in [7, 14, 28]:
        df[f'rolling_mean_{window}'] = df.groupby(keys)['units_sold'].shift(1).rolling(window).mean().reset_index(level=[0,1], drop=True)

    df = df.fillna(0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f'Feature store saved: {OUT} rows={len(df):,}')

if __name__ == '__main__':
    pandas_etl()
