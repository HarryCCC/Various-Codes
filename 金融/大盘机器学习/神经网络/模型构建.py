import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.callbacks import EarlyStopping

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
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, random_state=0)

# 将数据集的形状转换为适合LSTM的输入形状
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_train = np.array(X_train, dtype=np.float64)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
X_test = np.array(X_test, dtype=np.float64)

print("X_train shape:", X_train.shape)
print("X_train dtype:", X_train.dtype)
print("Y_train shape:", Y_train.shape)
print("Y_train dtype:", Y_train.dtype)

# 创建神经网络模型
model = Sequential()
model.add(LSTM(units=90, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(units=30))
model.add(Dense(1))

# 编译模型
model.compile(optimizer=Adam(learning_rate=0.001), loss=MeanSquaredError())

# 打印训练开始信息
print("Training started...")

# 定义早停回调
early_stopping = EarlyStopping(
    monitor='val_loss',  # 监控的指标
    patience=50,  # 忍受连续多少个epoch没有改善
    min_delta=0.001,  # 改善的最小变化量
    restore_best_weights=True  # 是否恢复到最佳权重
)

# 在模型训练时使用早停回调
model.fit(X_train, Y_train,
          epochs=1000,  # 可以设置一个较大的epochs数，因为早停会自动停止训练
          batch_size=32,
          verbose=1,
          validation_split=0.1,  # 从训练集中划分出10%作为验证集
          callbacks=[early_stopping]  # 应用早停回调
         )

# 打印训练结束信息
print("Training completed.")

# 保存模型
model.save('market_price_model.h5')

# 测试集上进行预测并评估模型性能
Y_pred = model.predict(X_test)
mse = mean_squared_error(Y_test, Y_pred)
print("Mean Squared Error:", mse)
