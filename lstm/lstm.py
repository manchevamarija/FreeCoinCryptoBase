import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from datetime import datetime, timedelta
import pandas as pd


def prepare_data(series, window=60):
    X, y = [], []
    for i in range(window, len(series)):
        X.append(series[i - window:i])
        y.append(series[i])
    return np.array(X), np.array(y)


def run_lstm_prediction(prices, dates, horizon_value=7, horizon_type="days"):
    # Convert prices to array
    prices = np.array(prices).reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(prices)

    window = 60
    X, y = prepare_data(scaled_prices, window)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)

    last_window = scaled_prices[-window:].reshape(1, window, 1)
    future_preds = []
    for _ in range(horizon_value):
        pred_scaled = model.predict(last_window, verbose=0)
        future_pred = scaler.inverse_transform(pred_scaled)[0][0]
        future_preds.append(float(future_pred))
        last_window = np.append(last_window[:, 1:, :], pred_scaled.reshape(1, 1, 1), axis=1)

    last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
    future_dates = []
    for i in range(1, horizon_value + 1):
        if horizon_type == "days":
            new_date = last_date + timedelta(days=i)
        elif horizon_type == "months":
            new_date = last_date + pd.DateOffset(months=i)
        elif horizon_type == "years":
            new_date = last_date + pd.DateOffset(years=i)
        future_dates.append(new_date.strftime("%Y-%m-%d"))

    return future_preds, future_dates
