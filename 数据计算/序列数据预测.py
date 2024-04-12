import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Historical data, in chronological order
data = [1.6,0.9,0.6,0.8,0.8,1.3,2.1,1.8,1.8,1.9,1.4,0.8,1.2,0.6]

# Number of periods to forecast
forecast_periods = 12


def forecast_data(data, forecast_periods):
    # Time series model
    arima_model = ARIMA(data, order=(1, 1, 1))
    arima_results = arima_model.fit()
    arima_pred = arima_results.forecast(steps=forecast_periods)

    # Regression model
    X = np.array(range(len(data))).reshape(-1, 1)
    y = np.array(data)
    reg_model = LinearRegression()
    reg_model.fit(X, y)
    reg_pred = reg_model.predict(np.array(range(len(data), len(data) + forecast_periods)).reshape(-1, 1))

    # Random forest model
    rf_model = RandomForestRegressor(n_estimators=100)
    rf_model.fit(X, y)
    rf_pred = rf_model.predict(np.array(range(len(data), len(data) + forecast_periods)).reshape(-1, 1))

    # Weighted average, the same weight is simply set here, which can be adjusted according to the performance of the model
    weights = [0.33, 0.34, 0.33]
    final_pred = weights[0] * arima_pred + weights[1] * reg_pred + weights[2] * rf_pred

    return final_pred


# Forecast future data
predicted_data = forecast_data(data, forecast_periods)

print(f"预测后{forecast_periods}个数据为: {predicted_data}")