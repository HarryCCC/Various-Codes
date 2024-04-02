import pandas as pd
from sklearn.metrics import r2_score

# 读取CSV文件
file_path = "CallOptionData_apple_2021-2023_with_BSM&NSDE.csv"
df = pd.read_csv(file_path)

# 去除包含NaN值的行
df = df.dropna(subset=['CallOptionPrice', 'BSM_Pricing', 'NeuralSDE_Pricing'])

# 计算平均绝对误差(MAE)
mae_bsm = abs(df['CallOptionPrice'] - df['BSM_Pricing']).mean()
mae_nsde = abs(df['CallOptionPrice'] - df['NeuralSDE_Pricing']).mean()

print("BSM平均绝对误差(MAE):", mae_bsm)
print("Neural SDE平均绝对误差(MAE):", mae_nsde)

if mae_bsm < mae_nsde:
    print("BSM模型的平均绝对误差(MAE)更小,拟合效果更佳。")
elif mae_nsde < mae_bsm:
    print("Neural SDE模型的平均绝对误差(MAE)更小,拟合效果更佳。")
else:
    print("两种模型的平均绝对误差(MAE)相等。")

print("\n")

# 计算均方误差(MSE)
mse_bsm = ((df['CallOptionPrice'] - df['BSM_Pricing']) ** 2).mean()
mse_nsde = ((df['CallOptionPrice'] - df['NeuralSDE_Pricing']) ** 2).mean()

print("BSM均方误差(MSE):", mse_bsm)
print("Neural SDE均方误差(MSE):", mse_nsde)

if mse_bsm < mse_nsde:
    print("BSM模型的均方误差(MSE)更小,拟合效果更佳。")
elif mse_nsde < mse_bsm:
    print("Neural SDE模型的均方误差(MSE)更小,拟合效果更佳。")
else:
    print("两种模型的均方误差(MSE)相等。")

print("\n")

# 计算平均绝对百分比误差(MAPE)
mape_bsm = (abs(df['CallOptionPrice'] - df['BSM_Pricing']) / df['CallOptionPrice']).mean() * 100
mape_nsde = (abs(df['CallOptionPrice'] - df['NeuralSDE_Pricing']) / df['CallOptionPrice']).mean() * 100

print("BSM平均绝对百分比误差(MAPE):", mape_bsm)
print("Neural SDE平均绝对百分比误差(MAPE):", mape_nsde)

if mape_bsm < mape_nsde:
    print("BSM模型的平均绝对百分比误差(MAPE)更小,拟合效果更佳。")
elif mape_nsde < mape_bsm:
    print("Neural SDE模型的平均绝对百分比误差(MAPE)更小,拟合效果更佳。")
else:
    print("两种模型的平均绝对百分比误差(MAPE)相等。")

print("\n")

# 计算R平方
r2_bsm = r2_score(df['CallOptionPrice'], df['BSM_Pricing'])
r2_nsde = r2_score(df['CallOptionPrice'], df['NeuralSDE_Pricing'])

print("BSM R平方:", r2_bsm)
print("Neural SDE R平方:", r2_nsde)

if r2_bsm > r2_nsde:
    print("BSM模型的R平方更高,拟合效果更佳。")
elif r2_nsde > r2_bsm:
    print("Neural SDE模型的R平方更高,拟合效果更佳。")
else:
    print("两种模型的R平方相等。")