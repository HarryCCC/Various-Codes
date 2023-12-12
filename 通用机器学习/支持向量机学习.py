# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC

# 生成一些随机的数据点
X = np.random.randn(200, 2) # 特征矩阵，每个样本有两个特征
y = np.logical_xor(X[:, 0] > 0, X[:, 1] > 0) # 目标向量，每个样本有一个目标值，是一个异或函数的结果

# 创建一个SVM模型的实例，使用径向基函数 (Radial Basis Function, RBF) 作为核函数
model = SVC(kernel="rbf")

# 使用数据点来训练模型
model.fit(X, y)

# 预测新的数据点的目标值
X_new = np.array([[0.5, 0.5], [-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5]]) # 新的特征矩阵，包含四个新的样本
y_pred = model.predict(X_new) # 预测的目标向量，包含四个预测的目标值
print(y_pred)

# 绘制数据点和模型的决策边界
plt.scatter(X[y==0, 0], X[y==0, 1], color="blue", label="Class 0") # 绘制类别为0的数据点
plt.scatter(X[y==1, 0], X[y==1, 1], color="red", label="Class 1") # 绘制类别为1的数据点
plt.scatter(X_new[:, 0], X_new[:, 1], color="green", marker="x", label="New samples") # 绘制新的样本点
xx, yy = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100)) # 创建一个网格
Z = model.decision_function(np.c_[xx.ravel(), yy.ravel()]) # 计算网格上每个点的决策函数值
Z = Z.reshape(xx.shape) # 调整形状
plt.contour(xx, yy, Z, levels=[0], colors="black") # 绘制决策边界
plt.xlabel("x1") # 设置x轴的标签
plt.ylabel("x2") # 设置y轴的标签
plt.legend() # 显示图例
plt.show() # 显示图像
