import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from skopt import BayesSearchCV
from skopt.callbacks import VerboseCallback
from skopt.utils import use_named_args

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
    'n_estimators': (100, 5000),            # 树的数量
    'max_depth': (3, 15),                   # 树的最大深度
    'min_samples_split': (2, 15),           # 内部节点再划分所需的最小样本数
    'min_samples_leaf': (1, 10),             # 叶子节点最少的样本数
    'max_features': ['sqrt', 'log2'],       # 寻找最佳分割点时考虑的特征数量
    'bootstrap': [True, False],             # 是否有放回抽样
    'max_leaf_nodes': (10, 500),            # 叶子节点的最大数量
    'min_weight_fraction_leaf': (0.0, 0.2)  # 叶子节点所需的最小权重分数
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

# 训练随机森林模型并进行贝叶斯优化
rf_model = RandomForestRegressor(random_state=42)
bayes_search = BayesSearchCV(estimator=rf_model, search_spaces=param_space, 
                             n_iter=100, cv=3, n_jobs=-1, verbose=2, scoring='neg_mean_squared_error', random_state=42)

# 自定义早停机制实例
early_stopper = CustomEarlyStopper(no_improvement_stop=5)
verbose_callback = VerboseCallback(n_total=100)

# 执行贝叶斯优化
try:
    bayes_search.fit(X_train_part, y_train_part, callback=[early_stopper, verbose_callback])
except StopIteration:
    print("Early stopping triggered, finishing search.")

# 输出最佳参数
best_params = bayes_search.best_params_
print(f'最佳参数组合: {best_params}')

# 使用最佳参数重新训练模型
rf_model_optimized = RandomForestRegressor(**best_params, random_state=42)
rf_model_optimized.fit(X_train_part, y_train_part)

# 模型评估
y_val_pred_rf = rf_model_optimized.predict(X_val_part)
mse_rf = mean_squared_error(y_val_part, y_val_pred_rf)
print(f'优化后的随机森林验证集上的均方误差: {mse_rf}')

# 保存优化后的随机森林模型
joblib.dump(rf_model_optimized, 'trained_rf_model_optimized.joblib')
