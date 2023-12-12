import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import joblib



# 加载数据
file_path = '合并数据.csv'  # 请更改为您的文件路径
data = pd.read_csv(file_path)

# 使用线性插值填充 NaN 值
data = data.infer_objects(copy=False)
data.interpolate(method='linear', inplace=True)


# 使用 pd.to_datetime 转换日期格式
data['date'] = pd.to_datetime(data['date'], format='%Y/%m/%d')  # 将字符串日期转换为 datetime 对象

# 提取年份和月份
data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data.drop(columns=['date'], inplace=True)


# 假设 "united-states-economic-growth-rate_quarterly_expanded_value" 是目标变量
X = data.drop(columns=['united-states-economic-growth-rate_quarterly_expanded_value'])
y = data['united-states-economic-growth-rate_quarterly_expanded_value']

# 数据预处理
scaler = StandardScaler()
X = scaler.fit_transform(X)

# 分割数据集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# 检查数据中是否有nan或inf
assert not pd.isna(X).any().any(), "X contains nan values"
assert not pd.isna(y).any(), "y contains nan values"

# 建立神经网络模型
model = Sequential([
    Dense(64, activation='relu', input_shape=(X_train.shape[1],)),  # 更改了神经元数量
    keras.layers.Dropout(0.3),  # 添加了 Dropout 层
    Dense(64, activation='relu'),  # 更改了神经元数量
    keras.layers.Dropout(0.3),  # 添加了 Dropout 层
    Dense(1)
])

# 编译模型
optimizer = keras.optimizers.Adam(learning_rate=0.0001)  # 调整了学习率
model.compile(optimizer=optimizer, loss='mse')

# 训练模型
model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_test, y_test))  # 调整了批次大小和周期数


# 预测
y_pred = model.predict(X_test)

# 评估模型
loss = model.evaluate(X_test, y_test)
print(f'Model Loss on Test Data: {loss}')


# 保存scaler
joblib.dump(scaler, 'scaler.pkl')
# 保存模型
model.save('model.h5')