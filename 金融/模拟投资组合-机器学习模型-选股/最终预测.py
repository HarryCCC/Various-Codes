import pandas as pd

# 读取第一个 Excel 文件
file1 = 'RF&XGBoost因子-预测结果.xlsx'
df1 = pd.read_excel(file1)

# 读取第二个 Excel 文件
file2 = 'LSTM&走势拟合-预测结果.xlsx'
df2 = pd.read_excel(file2)

# 提取股票名称和位置
df1['原始位置'] = df1.index
df2['原始位置'] = df2.index

# 重命名列以便合并
df1.rename(columns={'股票名称': '股票名称1'}, inplace=True)
df2.rename(columns={'股票名称': '股票名称2', '股票代码': '股票代码2'}, inplace=True)

# 查找交叉股票
common_stocks = pd.merge(df1[['股票名称1', '原始位置']], df2[['股票名称2', '原始位置', '股票代码2']], left_on='股票名称1', right_on='股票名称2')

# 计算位置总和
common_stocks['位置总和'] = common_stocks['原始位置_x'] + common_stocks['原始位置_y']

# 按位置总和排序
common_stocks_sorted = common_stocks.sort_values(by='位置总和')

# 选择所需的列，并重命名以便输出
output_df = common_stocks_sorted[['股票代码2', '股票名称1', '位置总和']].rename(columns={'股票代码2': '股票代码', '股票名称1': '股票名称'})

# 将结果输出到新的 Excel 文件
output_file = '最终预测结果.xlsx'
output_df.to_excel(output_file, index=False)
