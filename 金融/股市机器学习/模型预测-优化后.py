import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import numpy as np

'''
1. 跳过前两行读取
2. 读取前两列股票代码与股票名字信息
3. 跳过前两列读取
4. 筛选69-75每一列大于该列平均值
5. 删除零列
6. 读取每一行的前40个数据（跳过零单元格）
7. 翻转该前40列数据
'''

# 加载数据，跳过前两行
predicted_data_path = 'predict/predict_data.xlsx'
df = pd.read_excel(predicted_data_path, header=None, skiprows=2)

#筛风险回报和基本面
#filter_col_indices = range(84, 90) 
#只筛基本面
filter_col_indices = range(87, 90)

# 计算每列的平均值并筛选出同时满足条件的行
filter_conditions = [df[col] > df[col].mean() for col in filter_col_indices]
df = df[np.logical_and.reduce(filter_conditions)]
# 输出筛选后的行数
print(f"筛选后的行数: {df.shape[0]}")

# 提取股票代码和名称
stock_codes = df.iloc[:, 0].values
stock_names = df.iloc[:, 1].values

# 从第三列开始读取数据，直到遇到空白列
data_start_col = 2
first_blank_col = df.isnull().all().idxmax()
df = df.iloc[:, data_start_col:first_blank_col]

# 删除全为0的列
df = df.loc[:, (df != 0).any(axis=0)]

# 反转数据顺序，使其从旧到新
df = df.apply(lambda row: row[::-1], axis=1)



# 加载模型和归一化对象
model = load_model('model/trained_model.h5')
feature_scaler = joblib.load('model/feature_scaler.gz')
target_scaler = joblib.load('model/target_scaler.gz')

# 预测函数，重复进行预测并计算平均值
def repeated_rolling_predictions(data, model, feature_scaler, target_scaler, time_step, days=7, repeats=3):
    all_avg_predictions = []
    for _ in range(repeats):
        predictions = []
        current_data = data.copy()
        for _ in range(days):
            scaled_data = feature_scaler.transform(current_data[-time_step:].reshape(1, -1))
            scaled_data = scaled_data.reshape(1, time_step, 1)
            predicted = model.predict(scaled_data)
            predicted = target_scaler.inverse_transform(predicted).flatten()[0]
            predictions.append(predicted)

            current_data = np.append(current_data, predicted)[-time_step:]

        all_avg_predictions.append(np.mean(predictions))
    
    return np.mean(all_avg_predictions)

# 对每一行数据进行预测
results = []
for index, (code, name, row) in enumerate(zip(stock_codes, stock_names, df.values)):
    print(f"正在进行第 {index + 1} 行数据的预测: {code} {name}")

    # 检查行数据长度
    if len(row) < 40:
        print(f"跳过 {code} 的预测，因为数据长度不足40。")
        continue

    final_avg_prediction = repeated_rolling_predictions(row, model, feature_scaler, target_scaler, time_step=40, days=7, repeats=3)
    results.append((code, name, final_avg_prediction))


# 过滤掉任何包含NaN的预测结果
results = [(code, name, prediction) for code, name, prediction in results if not np.isnan(prediction)]
# 根据预测结果从大到小排序
results.sort(key=lambda x: x[2], reverse=True)

# 输出排序后的结果到txt文件
with open('predictions.txt', 'w') as file:
    # 首先输出预期结果最高的五只股票的代码
    file.write("Top 10 Predicted Stocks:\n")
    for stock in results[:10]:
        file.write(f"{stock[0]}\n")
    # 添加一个分隔符
    file.write("\nFull Predictions:\n")
    # 然后输出所有过滤掉NaN的完整列表
    for stock in results:
        file.write(f"{stock[0]} {stock[1]}: {stock[2]:.2f} (scaled_units)\n")