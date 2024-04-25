import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder, OneHotEncoder
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import LSTM, Dropout, Dense, Input, Concatenate
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import Sequence
import joblib

# === 可调整参数 ===
sequence_length = 32
lstm_units = 512
dropout_rate = 0.3
epochs = 1
batch_size = 64
test_size = 0.2
validation_split = 0.1
optimizer = 'rmsprop'

# === 数据预处理 ===
midi_data_path = 'cleaned_midi_data.csv' 
df = pd.read_csv(midi_data_path)

encoder = LabelEncoder()
df['note/chord_encoded'] = encoder.fit_transform(df['note/chord'].astype(str))

onehot_encoder = OneHotEncoder(sparse=False)
encoded_notes = onehot_encoder.fit_transform(df['note/chord_encoded'].values.reshape(-1, 1)).astype(np.float32)

scaler = MinMaxScaler()
df[['offset', 'duration', 'velocity']] = scaler.fit_transform(df[['offset', 'duration', 'velocity']])

split_index = int(len(df) * (1 - test_size))
train_data = df[:split_index]
test_data = df[split_index:]

# === 修改数据生成器 ===
class DataGenerator(Sequence):
    def __init__(self, df, batch_size=64, sequence_length=32, shuffle=True):
        self.df = df
        self.batch_size = batch_size
        self.sequence_length = sequence_length
        self.shuffle = shuffle
        self.indexes = np.arange(len(df) - sequence_length + 1)  # 调整索引以防越界
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __len__(self):
        return int(np.floor((len(self.df) - self.sequence_length + 1) / self.batch_size))

    def __getitem__(self, index):
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        X = np.empty((self.batch_size, self.sequence_length, encoded_notes.shape[1] + 3), dtype=np.float32)
        y = np.empty((self.batch_size, encoded_notes.shape[1] + 3), dtype=np.float32)

        for i, idx in enumerate(indexes):
            X[i, :, :-3] = encoded_notes[idx: idx + self.sequence_length]
            X[i, :, -3:] = self.df.iloc[idx: idx + self.sequence_length, :][['offset', 'duration', 'velocity']].values  # 使用 iloc 而不是 loc

            y_notes = encoded_notes[idx + self.sequence_length - 1]  # 调整索引
            y_others = self.df.iloc[idx + self.sequence_length - 1, :][['offset', 'duration', 'velocity']].values
            y[i] = np.concatenate([y_notes, y_others])

        return X, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.df) - self.sequence_length)
        if self.shuffle:
            np.random.shuffle(self.indexes)

train_generator = DataGenerator(train_data, batch_size=batch_size, sequence_length=sequence_length)
test_generator = DataGenerator(test_data, batch_size=batch_size, sequence_length=sequence_length, shuffle=False)

# === 模型构建 ===
model = Sequential()
model.add(LSTM(lstm_units, input_shape=(sequence_length, encoded_notes.shape[1] + 3), return_sequences=True))
model.add(Dropout(dropout_rate))
model.add(LSTM(lstm_units, return_sequences=False))
model.add(Dropout(dropout_rate))
model.add(Dense(encoded_notes.shape[1] + 3))  # 输出层大小应该是音符编码的大小加上3（offset, duration, velocity）

model.compile(loss='mse', optimizer=optimizer, metrics=['accuracy'])  # 使用均方误差作为损失函数

# === 模型训练与保存 ===
checkpoint_path = 'data/checkpoint_epoch_{epoch:02d}.h5'
checkpoint = ModelCheckpoint(checkpoint_path, save_best_only=False, period=1)
lr_reducer = ReduceLROnPlateau(factor=0.5, patience=5, min_lr=0.0001, verbose=1)

history = model.fit(train_generator, epochs=epochs, validation_data=test_generator, callbacks=[checkpoint, lr_reducer], verbose=2)


# 在这里我们将计算几何平均并选择最优模型
losses = history.history['loss']
val_losses = history.history['val_loss']
accuracies = history.history['accuracy']
val_accuracies = history.history['val_accuracy']
# 计算几何平均
gm_losses = [np.sqrt(l * vl) for l, vl in zip(losses, val_losses)]
gm_accuracies = [np.sqrt(a * va) for a, va in zip(accuracies, val_accuracies)]
# 标准化指标
normalized_gm_losses = (gm_losses - np.min(gm_losses)) / (np.max(gm_losses) - np.min(gm_losses))
normalized_gm_accuracies = (gm_accuracies - np.min(gm_accuracies)) / (np.max(gm_accuracies) - np.min(gm_accuracies))
# 计算得分
alpha = 0.2  # 假设损失和准确率同等重要
scores = [(1 - alpha) * (1 - ngl) + alpha * nga for ngl, nga in zip(normalized_gm_losses, normalized_gm_accuracies)]
# 选择得分最高的周期
best_epoch = np.argmax(scores)
print(f"在第 {best_epoch + 1} 个周期找到最佳模型，得分为 {scores[best_epoch]}")
# 根据选择的最佳周期来保存最优模型
if best_epoch == len(losses) - 1:
    # 如果最后一个周期就是最优周期，那么保存当前模型状态
    model.save('data/best_model.h5')
    print(f"最终模型已保存为 data/best_model.h5")
else:
    # 如果最优周期不是最后一个周期，那么我们加载并保存最优周期的模型
    best_model_path = f"data/checkpoint_epoch_{best_epoch + 1:02d}.h5"
    best_model = load_model(best_model_path)
    best_model.save('data/best_model.h5')
    print(f"最优模型已保存为 data/best_model.h5")
# 删除所有周期的模型文件
for epoch in range(1, epochs + 1):
    epoch_model_path = f"data/checkpoint_epoch_{epoch:02d}.h5"
    if os.path.exists(epoch_model_path):
        os.remove(epoch_model_path)

# 保存相关数据
joblib.dump(encoder, 'data/encoder.pkl')
joblib.dump(onehot_encoder, 'data/onehot_encoder.pkl')
joblib.dump(scaler, 'data/scaler.pkl')
np.save('data/sequence_length.npy', sequence_length)

print("训练完成。模型和相关数据已保存。")

