import pandas as pd
import numpy as np

# 读取 CSV 文件
df = pd.read_csv('sp500_data.csv', header=None, names=['Date', 'Value','Scaled'])

# 将第3列设置为数值型
df['Scaled'] = pd.to_numeric(df['Scaled'], errors='coerce')

# 将数据分成每 52 天一组
groups = [df['Scaled'][i:i+52] for i in range(0, len(df), 52)]

# 计算每组的平均值
group_means = [g.mean() for g in groups]

# 计算这些平均值的标准差
std_dev = np.std(group_means)

print(f"Standard Deviation (window size = 52): {std_dev}")