import pickle
import pandas as pd

# PKL文件路径
pkl_file_path = 'income_df_ori.pkl'
# 转换后CSV文件的保存路径
csv_file_path = 'output.csv'

# 使用pickle加载PKL文件
with open(pkl_file_path, 'rb') as file:
    # 假设PKL文件中存储的是一个Pandas DataFrame
    df = pickle.load(file)

# 将DataFrame保存为CSV文件
df.to_csv(csv_file_path, index=False)  # index=False表示不保存索引列

print(f"PKL文件已成功转换为CSV文件: {csv_file_path}")