import pandas as pd
from sklearn.decomposition import PCA
import numpy as np

# Read the Excel data
df = pd.read_excel('FINM3008 - Assignment Analysis S1 2024.xlsx', sheet_name='Qtr Returns', index_col=0, usecols=lambda x: x != 'US$ per A$1')

# Remove the first row
df = df.iloc[1:]

# Convert data to numeric type, non-numeric values to NaN
df = df.apply(pd.to_numeric, errors='coerce')

# 去除包含NaN的行
df.dropna(inplace=True)

# 对数据进行标准化处理
df_scaled = (df - df.mean()) / df.std()

# 对数据进行主成分分析
pca = PCA()
pca.fit(df_scaled)

# 输出主成分分析结果
print("Explained variance ratio:")
np.set_printoptions(suppress=True)  # 取消科学计数法
print(np.array2string(pca.explained_variance_ratio_, max_line_width=np.inf, precision=6))

print("\nPrincipal components:")
np.set_printoptions(suppress=True)  # 取消科学计数法
components_df = pd.DataFrame(pca.components_.T, index=df.columns)
print(components_df.to_string(max_rows=None, max_cols=None))


# 选取前8个主成分
n_components = 8
selected_components = components_df.iloc[:, :n_components]

# 计算每个主成分的均值
pc_mean = np.dot(df_scaled, selected_components)

# 计算每个主成分的均值的和
pc_mean_sum = np.sum(pc_mean, axis=0)

# 计算每种资产的预期收益率
expected_returns = np.dot(selected_components, pc_mean_sum)

# 对预期收益率进行反标准化处理
expected_returns_original = expected_returns * df.std() + df.mean()

# 将预期收益率转换为DataFrame
expected_returns_df = pd.DataFrame(expected_returns_original, index=df.columns, columns=['Expected Return'])
print("Expected Returns (Original Scale):")
print(expected_returns_df.to_string(max_rows=None))