import pandas as pd
import tensorflow as tf
import joblib
import numpy as np
from tqdm import tqdm

# 加载数据,跳过前两行
predicted_data_path = 'predict_data.xlsx'
df_predict = pd.read_excel(predicted_data_path, header=None, skiprows=2)

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

# 加载模型和归一化对象
model = tf.keras.models.load_model('model/trained_model.h5') 
feature_scaler = joblib.load('model/feature_scaler.gz')
target_scaler = joblib.load('model/target_scaler.gz')

# 预测函数,重复进行预测并计算平均值
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
for index, (code, name, row) in enumerate(zip(stock_codes, stock_names, df_predict.values)):
    print(f"正在进行第 {index + 1} 行数据的预测: {code} {name}")

    # 检查行数据长度
    if len(row) < 40:
        print(f"跳过 {code} 的预测,因为数据长度不足40。")
        continue

    final_avg_prediction = repeated_rolling_predictions(row, model, feature_scaler, target_scaler, time_step=40, days=7, repeats=3)
    results.append((code, name, final_avg_prediction))

# 过滤掉任何包含NaN的预测结果  
results = [(code, name, prediction) for code, name, prediction in results if not np.isnan(prediction)]
# 根据预测结果从大到小排序
results.sort(key=lambda x: x[2], reverse=True)

# 将预测结果保存为字典
predict_dict = {code: prediction for code, name, prediction in results}

# 计算综合得分
combined_scores = {code: rank + 1 for rank, (code, prediction) in enumerate(sorted(predict_dict.items(), key=lambda x: x[1], reverse=True))}

# 根据综合得分排序  
sorted_scores = sorted(combined_scores.items(), key=lambda x: x[1])

# 将前100支股票的预测结果输出到XLSX文件
top_100_results = sorted_scores[:100]
output_data = []
for code, score in top_100_results:
    name = stock_names[list(stock_codes).index(code)]
    prediction = predict_dict[code]
    output_data.append([code, name, prediction, score])

output_df = pd.DataFrame(output_data, columns=['股票代码', '股票名称', '预测周度收益率', '综合得分'])
output_df.to_excel('LSTM-预测结果.xlsx', index=False)
