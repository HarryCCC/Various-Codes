import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import joblib
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 数据和模型配置
file_path = 'train_stock_data.xlsx'
cleaned_file_path = 'train_cleaned_stock_data.csv'
model_file_path = "model/trained_model.h5"
feature_scaler_file = 'model/feature_scaler.gz'
target_scaler_file = 'model/target_scaler.gz'
time_step = 40
test_size = 0.1
batch_size = 16
epochs = 3
# 参数化LSTM和Dense层的units数
lstm_units_1 = 90
lstm_units_2 = 60
lstm_units_3 = 30
dense_units_1 = 30
dense_units_2 = 10
output_units = 1

# 第一部分：数据加载和预处理
# 加载数据，跳过前2行和前2列，并忽略列名
df = pd.read_excel(file_path, skiprows=2, header=None, usecols=lambda column: column not in [0, 1])

# 删除全为0的列
df = df.loc[:, (df != 0).any(axis=0)]

# 反转数据顺序，使其从旧到新
df = df.apply(lambda row: row[::-1], axis=1)

# 数据预处理 - 归一化
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(df)

# 保存归一化后的数据
pd.DataFrame(scaled_data).to_csv(cleaned_file_path, index=False, header=False)

# 第二部分：模型训练
# 加载清洗后的数据
df_cleaned = pd.read_csv(cleaned_file_path)
df_cleaned = df_cleaned.apply(lambda row: row[::-1], axis=1)
df_cleaned = df_cleaned.apply(lambda row: row.dropna().reset_index(drop=True), axis=1)

# 数据集构建函数
def create_dataset(dataframe, time_step):
    X_data, y_data = [], []
    for index, row in dataframe.iterrows():
        for i in range(len(row) - time_step):
            X_data.append(row[i:(i + time_step)].values)
            y_data.append(row[i + time_step])
    return np.array(X_data), np.array(y_data)

X, y = create_dataset(df_cleaned, time_step)

# 归一化处理
feature_scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = feature_scaler.fit_transform(X)

target_scaler = MinMaxScaler(feature_range=(0, 1))
y_scaled = target_scaler.fit_transform(y.reshape(-1, 1))

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=test_size, random_state=0)

# 重塑输入以为LSTM准备
X_train = X_train.reshape((X_train.shape[0], time_step, 1))
X_test = X_test.reshape((X_test.shape[0], time_step, 1))

# 构建模型
model = Sequential()
model.add(LSTM(lstm_units_1, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(lstm_units_2, return_sequences=True))
model.add(LSTM(lstm_units_3, return_sequences=False))
model.add(Dense(dense_units_1))
model.add(Dense(dense_units_2))
model.add(Dense(output_units))

model.compile(optimizer='adam', loss='mean_squared_error')

# 早停机制和模型保存
early_stopping = EarlyStopping(monitor='val_loss', patience=5)
model_checkpoint = ModelCheckpoint(model_file_path, save_best_only=True)

# 训练模型
model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, 
          validation_data=(X_test, y_test),
          callbacks=[early_stopping, model_checkpoint])

# 加载最佳模型
model.load_weights(model_file_path)

# 模型评估
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# 反归一化
train_predict = target_scaler.inverse_transform(train_predict)
test_predict = target_scaler.inverse_transform(test_predict)

# 计算均方误差
train_rmse = np.sqrt(mean_squared_error(y_train, train_predict))
test_rmse = np.sqrt(mean_squared_error(y_test, test_predict))

# 保存归一化对象
joblib.dump(feature_scaler, feature_scaler_file)
joblib.dump(target_scaler, target_scaler_file)
