from pathlib import Path
import pandas as pd

DATA = Path('data/processed/feature_store.csv')

def _load():
    return pd.read_csv(DATA, parse_dates=['date']) if DATA.exists() else pd.DataFrame()

def drift_report():
    df = _load()
    if df.empty:
        return {'message': 'No feature store found.'}
    recent = df[df['date'] >= df['date'].max() - pd.Timedelta(days=30)]
    older = df[df['date'] < df['date'].max() - pd.Timedelta(days=30)]
    checks=[]
    for col in ['price','discount_pct','inventory','weather_temp','units_sold']:
        r = recent[col].mean(); o = older[col].mean() if len(older) else r
        change = 0 if o == 0 else abs((r-o)/o)*100
        checks.append({'feature': col, 'baseline_mean': round(float(o),2), 'recent_mean': round(float(r),2), 'change_pct': round(float(change),2), 'status': 'DRIFT' if change > 20 else 'OK'})
    return {'drift_checks': checks}

def anomaly_report():
    df = _load()
    if df.empty:
        return {'anomalies': []}
    daily = df.groupby('date', as_index=False)['units_sold'].sum().sort_values('date')
    mean = daily['units_sold'].rolling(14).mean()
    std = daily['units_sold'].rolling(14).std().fillna(0)
    daily['z_score'] = (daily['units_sold'] - mean) / std.replace(0, 1)
    anomalies = daily[abs(daily['z_score']) > 2.5].tail(20)
    return {'anomalies': [{'date': str(r.date.date()), 'units_sold': int(r.units_sold), 'z_score': round(float(r.z_score),2)} for r in anomalies.itertuples()]}
