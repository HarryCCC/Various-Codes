# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier, plot_tree

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data # 特征矩阵，每个样本有四个特征
y = iris.target # 目标向量，每个样本有一个目标值，是鸢尾花的类别

# 创建一个决策树分类器的实例，使用基尼系数 (Gini Index) 作为分裂准则
model = DecisionTreeClassifier(criterion="gini")

# 使用数据点来训练模型
model.fit(X, y)

# 预测新的数据点的目标值
X_new = np.array([[5.1, 3.5, 1.4, 0.2], [6.7, 3.1, 4.4, 1.4], [6.3, 3.3, 6.0, 2.5]]) # 新的特征矩阵，包含三个新的样本
y_pred = model.predict(X_new) # 预测的目标向量，包含三个预测的目标值
print(y_pred)

# 绘制决策树的结构
plt.figure(figsize=(10, 10)) # 设置图像的大小
plot_tree(model, feature_names=iris.feature_names, class_names=iris.target_names, filled=True) # 绘制决策树
plt.show() # 显示图像
