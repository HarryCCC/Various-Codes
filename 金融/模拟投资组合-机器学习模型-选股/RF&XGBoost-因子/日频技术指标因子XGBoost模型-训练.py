import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from skopt import BayesSearchCV
from skopt.callbacks import VerboseCallback

# 读取数据
train_df = pd.read_excel('日频技术指标因子数据-训练.xlsx')

# 数据预处理
# 获取特征和目标
X_train = train_df.iloc[:, 2:-1]  # 从第三列到倒数第二列为特征
y_train = train_df.iloc[:, -1]    # 最后一列为目标

# 拆分训练集和验证集
X_train_part, X_val_part, y_train_part, y_val_part = train_test_split(X_train, y_train, test_size=0.1, random_state=42)

# 定义贝叶斯优化的参数空间
param_space = {
    'learning_rate': (0.001, 0.2),            # 初始学习率
    'max_depth': (3, 15),                    # 树的最大深度
    'subsample': (0.5, 1.0),                 # 子样本比例
    'colsample_bytree': (0.5, 1.0),          # 每棵树使用的特征比例
    'alpha': (0.0, 1.0),                     # L1正则化系数
    'lambda': (0.0, 1.0),                    # L2正则化系数
    'n_estimators': (100, 10000),             # 树的数量
}

# 自定义早停机制
class CustomEarlyStopper:
    def __init__(self, no_improvement_stop):
        self.no_improvement_stop = no_improvement_stop
        self.best_score = None
        self.counter = 0

    def __call__(self, result):
        current_score = result.func_vals[-1]
        if self.best_score is None or current_score < self.best_score:
            self.best_score = current_score
            self.counter = 0
        else:
            self.counter += 1
        if self.counter >= self.no_improvement_stop:
            print("No improvement for {} iterations, stopping search.".format(self.no_improvement_stop))
            return True

# 训练XGBoost模型并进行贝叶斯优化
xgb_model = XGBRegressor(objective='reg:squarederror', random_state=42, eval_metric='rmse', early_stopping_rounds=10)

bayes_search = BayesSearchCV(estimator=xgb_model, search_spaces=param_space, 
                             n_iter=100, cv=3, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error', random_state=42)

# 自定义早停机制实例
early_stopper = CustomEarlyStopper(no_improvement_stop=10)
verbose_callback = VerboseCallback(n_total=100)

# 执行贝叶斯优化
fit_params = {
    "eval_set": [(X_val_part, y_val_part)],
    "verbose": True,
}

try:
    bayes_search.fit(X_train_part, y_train_part, callback=[early_stopper, verbose_callback], **fit_params)
except StopIteration:
    print("Early stopping triggered, finishing search.")

# 输出最佳参数
best_params = bayes_search.best_params_
print(f'最佳参数组合: {best_params}')

# 使用最佳参数重新训练模型
xgb_model_optimized = XGBRegressor(**best_params, objective='reg:squarederror', random_state=42, eval_metric='rmse', early_stopping_rounds=3)
xgb_model_optimized.fit(X_train_part, y_train_part, eval_set=[(X_val_part, y_val_part)], verbose=True)

# 模型评估
y_val_pred_xgb = xgb_model_optimized.predict(X_val_part)
mse_xgb = mean_squared_error(y_val_part, y_val_pred_xgb)
print(f'优化后的XGBoost验证集上的均方误差: {mse_xgb}')

# 保存优化后的XGBoost模型
joblib.dump(xgb_model_optimized, 'trained_xgboost_model_optimized.joblib')
