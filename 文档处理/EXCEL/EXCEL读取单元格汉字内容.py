import pandas as pd
import re

# 读取Excel文件
file_path = '股价对齐数据-原始数据 - 副本 (2).xlsx'
df = pd.read_excel(file_path, sheet_name=None)  # 读取所有sheet

# 定义一个正则表达式来匹配汉字
chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]')

# 初始化一个变量来存储第一个包含汉字的单元格的信息
first_chinese_cell = None

# 遍历每个sheet和每个单元格
for sheet_name, sheet_data in df.items():
    for col in sheet_data.columns:
        for idx, value in sheet_data[col].items():  # 修改为items()
            if isinstance(value, str) and chinese_char_pattern.search(value):
                first_chinese_cell = (sheet_name, idx, col, value)
                break
        if first_chinese_cell:
            break
    if first_chinese_cell:
        break

# 输出第一个包含汉字的单元格的信息
if first_chinese_cell:
    sheet_name, row, col, value = first_chinese_cell
    print(f"First cell containing Chinese characters found:")
    print(f"Sheet: {sheet_name}")
    print(f"Row: {row + 1}")
    print(f"Column: {col}")
    print(f"Value: {value}")
else:
    print("No cell containing Chinese characters found.")
