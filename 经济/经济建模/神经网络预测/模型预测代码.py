import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
import joblib

# 加载scaler
path1 = r"C:\Users\11470\Desktop\scaler.pkl"
loaded_scaler = joblib.load(path1)
# 加载模型
path2 = r"C:\Users\11470\Desktop\model.h5"
loaded_model = keras.models.load_model(path2)



# 新的数据点
new_data = pd.DataFrame({
    '1-year-treasury-rate-yield-chart_monthly_value': [5],
    '10-year-treasury-bond-rate-yield-chart_monthly_value': [6],
    '30-year-fixed-mortgage-rate-chart_monthly_value': [8],
    '30-year-treasury-bond-rate-yield-chart_monthly_value': [7],
    '5-year-treasury-bond-rate-yield-chart_monthly_value': [6],
    'capacity-utilization-rate-historical-chart_monthly_value': [80],
    'debt-to-gdp-ratio-historical-chart_monthly_value': [100],
    'fed-funds-rate-historical-chart_monthly_value': [4],
    'historical-inflation-rate-by-year_monthly_expanded_value': [6],
    'industrial-production-historical-chart_monthly_value': [100],
    'national-debt-growth-by-year_monthly_expanded_value': [10],
    'retail-sales-historical-chart_monthly_value': [225000],
    'us-national-unemployment-rate_monthly_value': [5]
})

# 转换日期为年和月的形式
new_data['year'] = 2023
new_data['month'] = 10

# 用之前的scaler进行缩放
new_data_scaled = loaded_scaler.transform(new_data)


# 使用模型进行预测
prediction = loaded_model.predict(new_data_scaled)


# 输出预测结果
print(f"The predicted united-states-economic-growth-rate_quarterly_expanded_value is: {prediction[0][0]}")
