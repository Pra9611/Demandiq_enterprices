from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import tensorflow as tf

DATA = Path('data/processed/feature_store.csv')
MODEL_DIR = Path('models')
REPORTS = Path('reports')
FEATURES = ['price','discount_pct','competitor_price','inventory','weather_temp','rainfall_mm','holiday_flag','event_flag','day_of_week','month','is_weekend','price_gap','lag_1','lag_7','lag_14','lag_28','rolling_mean_7','rolling_mean_14','rolling_mean_28']
TARGET = 'units_sold'


def make_sequences(X, y, lookback=28, max_samples=120000):
    n = min(len(X)-lookback-1, max_samples)
    xs, ys = [], []
    for i in range(n):
        xs.append(X[i:i+lookback])
        ys.append(y[i+lookback])
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32)


def main():
    MODEL_DIR.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA, parse_dates=['date']).sort_values('date')
    if len(df) > 180000:
        df = df.sample(180000, random_state=42).sort_values('date')

    X = df[FEATURES].values
    y = df[TARGET].values.astype(np.float32)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    X_seq, y_seq = make_sequences(Xs, y)

    split = int(len(X_seq)*.8)
    X_train, X_test = X_seq[:split], X_seq[split:]
    y_train, y_test = y_seq[:split], y_seq[split:]

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(X_train.shape[1], X_train.shape[2])),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.Dropout(.2),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mae')
    model.fit(X_train, y_train, validation_split=.1, epochs=5, batch_size=256, verbose=1)

    pred = model.predict(X_test).reshape(-1)
    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    mape = float(np.mean(np.abs((y_test - pred) / np.maximum(y_test, 1))) * 100)
    residual_std = float(np.std(y_test - pred))

    model.save(MODEL_DIR/'demandiq_lstm.keras')
    joblib.dump(scaler, MODEL_DIR/'scaler.joblib')
    metadata = {'features': FEATURES, 'mae': mae, 'rmse': rmse, 'mape': mape, 'residual_std': residual_std}
    (MODEL_DIR/'metadata.json').write_text(json.dumps(metadata, indent=2))
    (REPORTS/'training_metrics.json').write_text(json.dumps(metadata, indent=2))
    print(metadata)

if __name__ == '__main__':
    main()
