# 导入所需的库
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score

# 生成一些模拟的数据，假设有两个特征和两个类别，类别不平衡
X = np.random.randn(1000, 2)
y = np.random.choice([0, 1], size=1000, p=[0.9, 0.1])

# 定义不同类别的代价，假设将类别0误判为类别1的代价为1，将类别1误判为类别0的代价为5
cost_matrix = np.array([[0, 1], [5, 0]])

# 定义不同样本的权重，根据代价矩阵和类别标签计算
sample_weight = np.array([cost_matrix[y[i], 1 - y[i]] for i in range(len(y))])

# 划分训练集和测试集
X_train, X_test = X[:800], X[800:]
y_train, y_test = y[:800], y[800:]
# 划分样本权重
sample_weight_train, sample_weight_test = sample_weight[:800], sample_weight[800:]

# 创建一个逻辑回归模型，使用样本权重作为参数
model = LogisticRegression()
model.fit(X_train, y_train, sample_weight=sample_weight_train)

# 在测试集上进行预测
y_pred = model.predict(X_test)

# 计算混淆矩阵，准确率和F1分数
cm = confusion_matrix(y_test, y_pred)
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

# 打印结果
print("Confusion matrix:")
print(cm)
print("Accuracy:", acc)
print("F1 score:", f1)
