import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

# 数据配置
file_path = 'train_stock_data.xlsx'  # 原始数据文件路径
cleaned_file_path = 'train_cleaned_stock_data.csv'  # 清洗后数据保存路径
scaler_file_path = 'model/scaler.gz'  # 归一化对象保存路径

# 加载数据，跳过前三行和前两列，并忽略列名
df = pd.read_excel(file_path, skiprows=3, header=None, usecols=lambda column: column not in [0, 1])

# 删除全为0的列
df = df.loc[:, (df != 0).any(axis=0)]

# 数据预处理 - 归一化
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(df)

# 保存归一化后的数据
pd.DataFrame(scaled_data).to_csv(cleaned_file_path, index=False, header=False)

# 保存MinMaxScaler对象
joblib.dump(scaler, scaler_file_path)