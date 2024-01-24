import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

# 加载训练好的模型
model = load_model('market_price_model.h5')

# 读取新的Excel文件
new_df = pd.read_excel('predict_price.xlsx')

# 从第3行和第4列开始读取加权平均指数
new_weighted_average_index = new_df.iloc[2:, 3]

# 将加权平均指数转换为numpy数组
new_data = new_weighted_average_index.values
# 清洗数据，去除零
new_data = new_data[new_data != 0]
# 由于我们只需要最后60个数据点，我们可以直接获取它们
last_60_data = new_data[-60:]

# 存储预测结果
predictions = []
# 滚动生成接下来14个时间序列的预测数据
for _ in range(14):
    # 使用最后60个数据点创建特征
    last_60_features = np.array([last_60_data])
    last_60_features = np.array(last_60_features, dtype=np.float64)

    # 获取模型的输入形状
    n = model.layers[0].input_shape[1]
    m = model.layers[0].input_shape[2]
    # 调整 last_60_features 的形状
    last_60_features = np.expand_dims(last_60_features, axis=0)
    last_60_features = last_60_features.reshape((1, n, m))

    # 使用模型进行预测
    prediction = model.predict(last_60_features)
    
    # 将预测值添加到预测结果列表中
    predictions.append(prediction[0])
    
    # 更新最后60个数据点，将最新的预测值添加到列表中
    last_60_data = np.append(last_60_data[1:], prediction[0])
# 输出预测结果
print("Predicted next 14 values:", predictions)

# 打开文件用于写入
with open('predictions.txt', 'w') as file:
    # 将预测结果写入文件
    file.write("Predicted next 14 values:\n")
    for prediction in predictions:
        file.write(str(prediction) + '\n')
