import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib

# 读取数据
train_df = pd.read_excel('日频技术指标因子数据-训练.xlsx')

# 数据预处理
# 获取特征和目标
X_train = train_df.iloc[:, 2:-1]  # 从第三列到倒数第二列为特征
y_train = train_df.iloc[:, -1]    # 最后一列为目标

# 拆分训练集和验证集
X_train_part, X_val_part, y_train_part, y_val_part = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# 随机森林参数
rf_params = {
    'n_estimators': 200,           # 树的数量
    'max_depth': 10,               # 树的最大深度
    'min_samples_split': 2,        # 内部节点再划分所需的最小样本数
    'min_samples_leaf': 1,         # 叶子节点最少的样本数
    'max_features': 'sqrt',        # 寻找最佳分割点时考虑的特征数量
    'bootstrap': True,             # 是否有放回抽样
    'random_state': 42             # 随机种子
}

# 训练随机森林模型
rf_model = RandomForestRegressor(**rf_params)

rf_model.fit(X_train_part, y_train_part)

# 模型评估
y_val_pred_rf = rf_model.predict(X_val_part)
mse_rf = mean_squared_error(y_val_part, y_val_pred_rf)
print(f'随机森林验证集上的均方误差: {mse_rf}')

# 保存随机森林模型
joblib.dump(rf_model, 'trained_rf_model.joblib')
