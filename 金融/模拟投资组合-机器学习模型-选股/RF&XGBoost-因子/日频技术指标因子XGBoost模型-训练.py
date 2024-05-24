import pandas as pd
from xgboost import XGBRegressor
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

# XGBoost参数
xgb_params = {
    'learning_rate': 0.1,          # 初始学习率
    'max_depth': 5,                # 树的最大深度
    'subsample': 0.8,              # 子样本比例
    'colsample_bytree': 0.8,       # 每棵树使用的特征比例
    'objective': 'reg:squarederror',  # 目标函数：平方误差
    'random_state': 42,            # 随机种子
    'alpha': 0.001,                # L1正则化系数
    'lambda': 0.001,               # L2正则化系数
    'n_estimators': 100,           # 树的数量
    'early_stopping_rounds': 3,   # 早停轮数
    'eval_metric': 'rmse'          # 评估指标：均方根误差
}

# 训练模型
xgb_model = XGBRegressor(**xgb_params)

xgb_model.fit(X_train_part, y_train_part,
              eval_set=[(X_train_part, y_train_part), (X_val_part, y_val_part)],
              verbose=True)

# 模型评估
y_val_pred_xgb = xgb_model.predict(X_val_part)
mse_xgb = mean_squared_error(y_val_part, y_val_pred_xgb)
print(f'XGBoost验证集上的均方误差: {mse_xgb}')

# 保存XGBoost模型
joblib.dump(xgb_model, 'trained_xgboost_model.joblib')
