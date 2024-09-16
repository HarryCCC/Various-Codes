import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 只显示错误信息

import tensorflow as tf
tf.get_logger().setLevel('ERROR')  # 设置日志级别为只显示错误

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
from tqdm import tqdm  # 用于显示进度条

# 配置部分：模型参数和训练超参数
CONFIG = {
    'layers': [
        {'type': 'LSTM', 'units': 100, 'return_sequences': True},  # 第一层LSTM
        {'type': 'Dropout', 'rate': 0.2},                         # Dropout层
        {'type': 'LSTM', 'units': 50, 'return_sequences': True},  # 第二层LSTM
        {'type': 'Dropout', 'rate': 0.2},                         # Dropout层
        {'type': 'LSTM', 'units': 30, 'return_sequences': False}, # 第三层LSTM
        {'type': 'Dense', 'units': 1}  # 输出层
    ],
    'learning_rate': 0.01,   # 初始学习率
    'epochs': 100,            # 训练周期数
    'batch_size': 64,         # 每个批次的样本数量
    'patience': 3,            # EarlyStopping的耐心值
    'reduce_lr_patience': 3,  # ReduceLROnPlateau的耐心值
    'reduce_lr_factor': 0.5,  # ReduceLROnPlateau的学习率缩减因子
}

def clean_data(file_path):
    """
    清洗数据：删除除了第一行以外，其余行都是0的列。
    :param file_path: Excel文件路径
    :return: 清洗后的DataFrame
    """
    print("读取数据...")
    data = pd.read_excel(file_path)
    print("数据预览：")
    print(data.head())  # 显示前几行数据以检查格式

    # 检查数据框的形状
    print(f"初始数据形状：{data.shape}")

    # 数据清洗
    data_cleaned = data.loc[:, (data.iloc[1:] != 0).any(axis=0)]
    print(f"数据清洗完成，剩余{data_cleaned.shape[1]}列有效数据。")
    return data_cleaned

def preprocess_data(data_cleaned, window_size=30):
    """
    数据预处理：创建合并所有股票数据的滚动窗口数据集。
    :param data_cleaned: 清洗后的所有股票数据
    :param window_size: 滚动窗口大小
    :return: 训练集和测试集
    """
    X, y = [], []
    
    # 遍历每只股票的行数据
    for i in range(len(data_cleaned)):
        stock_data = data_cleaned.iloc[i, 2:].values  # 使用iloc获取时间序列数据，从第三列开始
        
        # 创建滚动窗口数据
        stock_X, stock_y = [], []
        for j in range(len(stock_data) - window_size):
            stock_X.append(stock_data[j:j + window_size])
            stock_y.append(stock_data[j + window_size])
        
        # 合并该股票的数据
        X.extend(stock_X)
        y.extend(stock_y)
    
    X = np.array(X)
    y = np.array(y)
    
    # 划分训练集和测试集
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"数据预处理完成，训练集大小：{X_train.shape}, 测试集大小：{X_test.shape}")
    return X_train, X_test, y_train, y_test

def build_lstm_model(input_shape):
    """
    构建LSTM模型。
    :param input_shape: 输入数据的形状
    :return: 编译后的LSTM模型
    """
    model = Sequential()
    
    # 动态添加层
    for idx, layer in enumerate(CONFIG['layers']):
        if layer['type'] == 'LSTM':
            # Prepare arguments for the LSTM layer
            lstm_args = {
                'units': layer['units'],
                'return_sequences': layer['return_sequences'],
            }
            # Only add input_shape for the first layer
            if idx == 0:
                lstm_args['input_shape'] = input_shape
            model.add(LSTM(**lstm_args))
        elif layer['type'] == 'Dense':
            model.add(Dense(units=layer['units']))
        elif layer['type'] == 'Dropout':
            model.add(Dropout(rate=layer['rate']))

    # 使用配置中的学习率
    optimizer = Adam(learning_rate=CONFIG['learning_rate'])
    model.compile(optimizer=optimizer, loss='mean_squared_error')
    
    print("模型构建完成。")
    return model

def train_and_evaluate_model(X_train, y_train, X_test, y_test):
    """
    训练LSTM模型并评估其性能。
    :param X_train: 训练特征集
    :param y_train: 训练标签集
    :param X_test: 测试特征集
    :param y_test: 测试标签集
    :return: 模型的MSE误差和训练好的模型
    """
    # 归一化数据
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 调整数据形状
    X_train_scaled = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
    X_test_scaled = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))

    # 构建LSTM模型
    model = build_lstm_model((X_train_scaled.shape[1], 1))

    # 定义回调函数
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=CONFIG['reduce_lr_factor'],
                                  patience=CONFIG['reduce_lr_patience'], min_lr=1e-6, verbose=0)
    early_stopping = EarlyStopping(monitor='val_loss', patience=CONFIG['patience'], verbose=0, restore_best_weights=True)

    print("开始训练模型...")
    # 训练模型
    model.fit(X_train_scaled, y_train, 
              epochs=CONFIG['epochs'], 
              batch_size=CONFIG['batch_size'], 
              validation_data=(X_test_scaled, y_test),
              callbacks=[reduce_lr, early_stopping], 
              verbose=1)

    print("训练完成，开始预测...")
    # 预测并计算误差
    y_pred = model.predict(X_test_scaled, verbose=0)
    mse = mean_squared_error(y_test, y_pred)
    print(f"模型评估完成，MSE误差：{mse}")
    
    # 保存模型
    model.save('lstm_general_model.h5')
    print("通用模型已保存为 lstm_general_model.h5")
    
    return mse

def main(file_path):
    """
    主函数：加载数据，清洗数据，使用LSTM模型进行时间序列预测。
    :param file_path: Excel文件路径
    """
    # 数据清洗
    data_cleaned = clean_data(file_path)

    # 数据预处理
    X_train, X_test, y_train, y_test = preprocess_data(data_cleaned)

    # 训练模型并评估性能
    mse = train_and_evaluate_model(X_train, y_train, X_test, y_test)

    print(f"通用LSTM模型的MSE误差：{mse}")

if __name__ == "__main__":
    file_path = 'StockReturnData.xlsx'  # 替换为你的Excel文件路径
    main(file_path)
