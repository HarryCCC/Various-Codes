import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

def predict_gdp_growth(model, intercept, coefficients, input_values):
    if len(input_values) != len(coefficients):
        return "The length of input values must match the number of coefficients."
    
    prediction = intercept
    for i in range(len(coefficients)):
        prediction += coefficients[i] * input_values[i]
        
    return prediction

# Load the data
file_path = "合并数据.csv"  # Replace this with the actual path to your file
df = pd.read_csv(file_path)

# Fill missing values with the average of the previous and next value in the column
for col in df.columns:
    for i, val in enumerate(df[col]):
        if pd.isna(val):
            prev_val = df[col].iloc[i-1] if i > 0 else 0
            next_val = df[col].iloc[i+1] if i < len(df[col]) - 1 else 0
            avg_val = (prev_val + next_val) / 2
            df.at[i, col] = avg_val

# 预处理：使用插值处理NaN值
df.fillna(df.interpolate(), inplace=True)

# 如果 'date' 列存在，去除它（或者将其转换为数值型）
if 'date' in df.columns:
    df.drop('date', axis=1, inplace=True)

# 分离特征（X）和目标变量（y）
X = df.drop('united-states-economic-growth-rate_quarterly_expanded_value', axis=1)
y = df['united-states-economic-growth-rate_quarterly_expanded_value']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
reg = LinearRegression()
reg.fit(X_train, y_train)

# Test the model
y_pred = reg.predict(X_test)

# Model evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R² Value: {r2}")

# Model coefficients and intercept
print(f"Intercept: {reg.intercept_}")
print(f"Coefficients: {reg.coef_}")


# Example usage: Predict GDP growth with custom input values
# Replace the array below with your actual input values
'''
参数说明：市场利率，1/5/10/30年期国债，30年抵押，
         通胀，债务GDP比例，国家债务增长率，产能利用率(最高100)，
         工业指数(基准100)，实际零售数额(m$)，失业率，人口增速

'''
input_values = [4, 5, 4, 5, 6, 7,    \
                 5, 120, 5, 80,    \
                100, 230000, 3, 0.35]
predicted_growth = predict_gdp_growth(reg, reg.intercept_, reg.coef_, input_values)
print(f"Predicted GDP Growth: {predicted_growth}")
