import pandas as pd
import numpy as np

# 读取Excel文件
file_path = 'FINM3008 - Assignment Analysis S1 2024.xlsx'
sheet_name = 'Beta Exposure Analysis'
df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)

# 提取市场指数收益率和各类资产收益率
market_returns = df.iloc[:, 4]  # E列
asset_returns = df.iloc[:, 7:22]  # H列到V列

# 计算每类资产关于市场指数的beta值
betas = {}
for column in asset_returns.columns:
    asset_return = asset_returns[column]
    covariance = np.cov(market_returns, asset_return)[0, 1]
    market_variance = np.var(market_returns)
    beta = covariance / market_variance
    betas[column] = beta

# 打印每类资产的beta值
for asset, beta in betas.items():
    print(f"{asset}: {beta:.4f}")