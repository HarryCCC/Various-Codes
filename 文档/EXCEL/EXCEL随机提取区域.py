import pandas as pd
import numpy as np

# 读取Excel文件
file_path = '股价对齐数据-原始数据 - 副本 (2).xlsx'
df = pd.read_excel(file_path)

# 确定可选区域的最大起始点
max_row_start = df.shape[0] - 10
max_col_start = df.shape[1] - 10

# 随机选择起始点
start_row = np.random.randint(0, max_row_start)
start_col = np.random.randint(0, max_col_start)

# 获取10x10的区域
selected_area = df.iloc[start_row:start_row + 10, start_col:start_col + 10]

# 打印所选区域
print("随机选择的10x10区域起始点：(行{}, 列{})".format(start_row, start_col))
print(selected_area)
