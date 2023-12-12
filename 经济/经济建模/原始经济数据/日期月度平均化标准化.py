import pandas as pd
import os
from datetime import datetime

# 获取当前工作目录下所有CSV文件
csv_files = [f for f in os.listdir() if f.endswith('.csv')]

# 遍历所有CSV文件并执行编辑操作
for csv_file in csv_files:
    try:
        # 根据文件名构建输出文件名
        output_filename = csv_file.split('.')[0] + '_monthly.csv'

        # 读取CSV文件，跳过前16行并强制列名
        df = pd.read_csv(csv_file, skiprows=16, names=['date', 'value'])

        # 删除列名中可能存在的多余空格
        df.columns = [col.strip() for col in df.columns]

        # 将 'date' 列转换为 datetime 对象
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # 删除日期转换失败的行
        df = df.dropna(subset=['date'])

        # 提取年份和月份到一个新列
        df['year_month'] = df['date'].dt.to_period('M')

        # 按 'year_month' 分组，并计算均值
        df_grouped = df.groupby('year_month').mean().reset_index()

        # 将 'year_month' 列转换为字符串格式，并保存在 'date' 列中
        df_grouped['date'] = df_grouped['year_month'].astype(str)

        # 只保留 'date' 和 'value' 列
        df_grouped = df_grouped[['date', 'value']]

        # 保存到一个新的 CSV 文件
        df_grouped.to_csv(output_filename, index=False)

        # 重新打开CSV文件并添加文档名
        document_name = csv_file.split('.')[0]
        with open(output_filename, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(f"{document_name}\n" + content)

    except Exception as e:
        print(f"An error occurred while processing {csv_file}: {e}")
