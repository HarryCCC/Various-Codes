import pandas as pd
import numpy as np

# 读取Excel文件中的Qtr Returns表，跳过前两行并忽略第一列和最后一列
df = pd.read_excel('FINM3008 - Assignment Analysis S1 2024.xlsx', sheet_name='Qtr Returns', skiprows=2, usecols="B:P")
# 打印列名以确认数据帧的结构
print(df.columns)
# 移除包含缺失值的行
df.dropna(inplace=True)

# 现有投资组合权重
current_weights = np.array([
0.12,
0.06,
0.17,
0.03,
0.01,
0.04,
0.08,
0.08,
0.03,
0.03,
0.05,
0.07,
0.1,
0.06,
0.07,

])

# 基准投资组合权重
benchmark_weights = np.array([
    0.27,  # Australian Equities (AE)
    0.10,  # World Equities, Unhedged (WE,U)
    0.09,  # World Equities, Hedged (WE,H)
    0.03,  # Emerging Markets (EM)

    0.00,  # World Listed Property (WLP)
    0.05,  # Australian Listed Property (ALP)
    0.05,  # Australian Direct Property (ADP)
    0.00,  # Commodities (CCFs) (COM)
    0.00,  # Gold (CCFs) (GD)
    0.05,  # Hedge Funds (HF)
    0.15,  # US Private Equity (PE)

    0.09,  # Australian Fixed Income (AFI)
    0.03,  # Australian Index-Linked Bonds (ILB)
    0.02,  # World Fixed Income (Hedged) (WFI)
    0.07,  # Australian Cash (AC)
])

# 计算两个投资组合每一期的预期回报
benchmark_returns = df.dot(benchmark_weights)
current_returns = df.dot(current_weights)

# 计算Tracking Error
differences = current_returns - benchmark_returns
tracking_error = np.sqrt(np.mean(differences**2))

print(f"Tracking Error: {100*tracking_error:.4f}{'%'}")
