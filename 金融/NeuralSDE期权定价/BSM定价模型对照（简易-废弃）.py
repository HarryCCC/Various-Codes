import numpy as np
from scipy.stats import norm

def bs_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# 期权参数
S = 1  # 标的价格
K = 1.013  # 行权价
T = 0.36  # 到期时间 
r = 0.025  # 无风险利率
sigma = 0.105  # 波动率

option_price = bs_call(S, K, T, r, sigma)
print(f"BSM Option Price: {option_price:.4f}")