import pandas as pd
import joblib
import numpy as np

# 读取数据
predict_df = pd.read_excel('日频技术指标因子数据-预测.xlsx')

# 保存股票代码和股票名称
stock_info = predict_df.iloc[:, :2]  # 前两列是股票代码和股票名称

# 数据预处理
# 获取特征
X_predict = predict_df.iloc[:, 2:]  # 预测数据中从第三列开始为特征

# 加载训练好的模型
xgb_model = joblib.load('trained_xgboost_model.joblib')
rf_model = joblib.load('trained_rf_model.joblib')

# 重复进行双重加权预测三次，并取平均值
predictions = []

for _ in range(3):
    y_pred_xgb = xgb_model.predict(X_predict)
    y_pred_rf = rf_model.predict(X_predict)
    y_pred_ensemble = (y_pred_xgb + y_pred_rf) / 2
    predictions.append(y_pred_ensemble)

# 计算平均预测值
average_predictions = np.mean(predictions, axis=0)

# 将预测结果添加到stock_info表中
stock_info['预测周度收益率'] = average_predictions

# 结果从大到小进行排序
sorted_stock_info = stock_info.sort_values(by='预测周度收益率', ascending=False)

# 保存预测结果到新的XLSX文件
sorted_stock_info.to_excel('RF&XGBoost因子-预测结果.xlsx', index=False)
