import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from tqdm import tqdm  # 用于显示进度条

# 读取历史数据
df_history = pd.read_csv('train_cleaned_stock_data.csv', header=None)

# 定义窗口大小和预测天数
window_size = 30
next_5_days = 5

# 预计算所有30日片段的特征向量
feature_vectors = []
return_values = []

print("Calculating feature vectors...")
for _, history_data in tqdm(df_history.iterrows(), total=df_history.shape[0]):
    for start_index in range(len(history_data) - window_size - next_5_days + 1):
        window_data = history_data[start_index : start_index + window_size]
        feature_vectors.append(window_data.values)
        
        next_5_days_data = history_data[start_index + window_size : start_index + window_size + next_5_days]
        if next_5_days_data.iloc[0] != 0:
            total_return = (next_5_days_data.iloc[-1] - next_5_days_data.iloc[0]) / next_5_days_data.iloc[0]
        else:
            total_return = np.nan
        return_values.append(total_return)

print("Feature vector calculation completed.")

# 读取并处理predict_data.xlsx中的数据
predicted_data_path = 'predict_data.xlsx'
df_predict = pd.read_excel(predicted_data_path, header=None, skiprows=2)

# 筛选个股
filter_col_indices1 = range(87, 89)  # 基本面-前60%
filter_col_indices2 = range(84, 86)  # 风险收益-前60%
# 筛选出同时满足条件的行
filter_conditions1 = [df_predict[col] >= df_predict[col].quantile(0.4) for col in filter_col_indices1]
filter_conditions2 = [df_predict[col] >= df_predict[col].quantile(0.4) for col in filter_col_indices2]
# 合并两个筛选条件
combined_filter_conditions = filter_conditions1 + filter_conditions2
# 应用筛选条件
df_predict = df_predict[np.logical_and.reduce(combined_filter_conditions)]
# 输出筛选后的行数
print(f"筛选后的行数: {df_predict.shape[0]}")

# 提取股票代码和名称
stock_codes = df_predict.iloc[:, 0].values
stock_names = df_predict.iloc[:, 1].values

# 从第三列开始读取数据,直到遇到空白列
data_start_col = 2
first_blank_col = df_predict.isnull().all().idxmax()
df_predict = df_predict.iloc[:, data_start_col:first_blank_col]

# 删除全为0的列
df_predict = df_predict.loc[:, (df_predict != 0).any(axis=0)]

# 反转数据顺序,使其从旧到新
df_predict = df_predict.apply(lambda row: row[::-1], axis=1)

# 读取train_cleaned_stock_data.csv中的历史数据
df_history = pd.read_csv('train_cleaned_stock_data.csv', header=None)

# 定义窗口大小
window_size = 30
next_5_days = 5

# 对每支股票,找到与其最近30天走势最接近的10段历史30天片段,并计算这10段历史片段之后5天的总收益率
results = []
for i, (code, name, predict_data) in enumerate(zip(stock_codes, stock_names, df_predict.values)):
    print(f"Processing stock {i + 1}/{len(stock_codes)}: {code} {name}")
    
    latest_30_days = predict_data[-window_size:]
    distances = euclidean_distances([latest_30_days], feature_vectors)[0]
    
    top_10_indices = distances.argsort()[:10]
    top_10_distances = distances[top_10_indices]
    top_10_returns = [return_values[i] for i in top_10_indices]
    
    avg_total_return = np.nanmean(top_10_returns)
    
    results.append((code, name, avg_total_return, list(zip(top_10_distances, top_10_returns))))

# 根据平均总收益率从大到小排序
results.sort(key=lambda x: x[2], reverse=True)

# 输出结果到txt文件
with open('predict/pattern_matching.txt', 'w') as file:
    file.write("Top 10 stocks by predicted 5-day return:\n")
    for stock in results[:10]:
        file.write(f"{stock[0]} {stock[1]}: {stock[2]*100:.2f}%\n")

    file.write("\nFull results:\n")
    for stock in results:
        file.write(f"{stock[0]} {stock[1]}: Predicted 5-day return {stock[2]*100:.2f}%\n")
        for match in stock[3]:
            file.write(f"  Closest match distance {match[0]:.2f}, 5-day return {'N/A' if np.isnan(match[1]) else f'{match[1]*100:.2f}%'}\n")