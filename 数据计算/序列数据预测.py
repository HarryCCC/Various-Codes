import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

# Historical data, in chronological order
data = [

-0.229466017053694,
0.180966108693328,
-0.024586079292602,
0.0430418553911363,
-0.216424011136073,
0.185101131049974,
-0.0425515419929923,
0.0670358240798539,
-0.248423034376321,
0.146945218980459,
-0.143727685007653,
0.114839669143551,
-0.267900861452407,
0.132358698542159,
-0.117827355021738,
0.101113376088511,
-0.204835381980473,
0.205345992170731,
-0.0726307510913617,
0.11763592433052,
-0.201666358665618,
0.200977158971449,
-0.0831668073611809,
0.129695963220831,
-0.219865319853643,
0.205225792023029,
-0.116337185272432,
0.094366316833181,
-0.225293309048755,
0.145726908652174,
-0.137529996018211,
0.148526017804558,
-0.151428058346363,
0.2529552339421,
-0.1049752970415,
0.145585908587867,
-0.178365542456701,
0.23901192634837,
-0.0947557175501181,
0.172484691190125,
-0.166731986420418,
0.272161531864624,
-0.1238455878969,
0.131909898236961,






]

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
# Set print options to display the array in one line
np.set_printoptions(linewidth=150)
print(f"预测后{forecast_periods}个数据为: {np.array2string(predicted_data, separator=',')}")