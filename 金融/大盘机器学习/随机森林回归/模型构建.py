import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump

# 读取Excel文件
df = pd.read_excel('market_price.xlsx')

# 从第3行和第4列开始读取加权平均指数
weighted_average_index = df.iloc[2:, 3]

# 将加权平均指数转换为numpy数组
data = weighted_average_index.values
# 清洗数据，去除零
data = data[data != 0]

# 使用滑动窗口方法创建特征和标签
def create_dataset(data, window_size=60):
    X, Y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        Y.append(data[i+window_size])
    return np.array(X), np.array(Y)

window_size = 60
X, Y = create_dataset(data, window_size)

# 划分数据集
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

# 训练随机森林回归模型
model = RandomForestRegressor(n_estimators=100, random_state=0, verbose=1)

# 打印训练开始信息
print("Training started...")

# 训练模型
model.fit(X_train, Y_train)

# 打印训练结束信息
print("Training completed.")

# 保存模型
dump(model, 'market_price_model.joblib')

# 测试集上进行预测并评估模型性能
Y_pred = model.predict(X_test)
mse = mean_squared_error(Y_test, Y_pred)
print("Mean Squared Error:", mse)