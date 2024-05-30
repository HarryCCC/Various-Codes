import pandas as pd
import os

def analyze_excel(file_path):
    # 读取Excel文件
    df = pd.read_excel(file_path)

    # 计算最长和最短的列
    max_col_length = df.count().max()
    min_col_length = df.count().min()
    max_col_position = df.count().idxmax()
    min_col_position = df.count().idxmin()

    # 计算最长和最短的行
    max_row_length = df.apply(lambda x: x.count(), axis=1).max()
    min_row_length = df.apply(lambda x: x.count(), axis=1).min()
    max_row_position = df.apply(lambda x: x.count(), axis=1).idxmax()
    min_row_position = df.apply(lambda x: x.count(), axis=1).idxmin()

    return max_col_position, max_col_length, min_col_position, min_col_length, max_row_position, max_row_length, min_row_position, min_row_length

# 指定文件路径
file_path = 'train_stock_data.xlsx' 

# 调用函数并打印结果
max_col_pos, max_col_len, min_col_pos, min_col_len, max_row_pos, max_row_len, min_row_pos, min_row_len = analyze_excel(file_path)
print(f"最长列的位置：{max_col_pos}, 长度：{max_col_len}")
print(f"最短列的位置：{min_col_pos}, 长度：{min_col_len}")
print(f"最长行的位置：{max_row_pos}, 长度：{max_row_len}")
print(f"最短行的位置：{min_row_pos}, 长度：{min_row_len}")
