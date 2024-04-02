import numpy as np
import pandas as pd
from scipy.stats import norm

def bsm_call_option_price(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

# 读取CSV文件
file_path = "CallOptionData_apple_2021-2023.csv"
df = pd.read_csv(file_path)

# 提取所需列
S = df['StockPrice']
K = df['StrikePrice']
T = df['YearToMaturity']
r = 0.045
sigma = df['ImpliedVolatility'] / 100  # 将隐含波动率从百分比转换为小数

# 计算BSM期权价格
bsm_prices = bsm_call_option_price(S, K, T, r, sigma)

# 将BSM期权价格添加到数据框中
df['BSM_Pricing'] = bsm_prices

# 保存更新后的数据框到新的CSV文件
output_path = "CallOptionData_apple_2021-2023_with_BSM.csv"
df.to_csv(output_path, index=False)