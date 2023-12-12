# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.metrics import euclidean_distances

# 加载鸢尾花数据集
iris = load_iris()
X = iris.data # 特征矩阵，每个样本有四个特征
y = iris.target # 目标向量，每个样本有一个目标值，是鸢尾花的类别

# 定义一个最近邻分类器的类
class NearestNeighborClassifier:

  # 初始化方法，设置最近邻的个数
  def __init__(self, n_neighbors=1):
    self.n_neighbors = n_neighbors # 最近邻的个数

  # 训练方法，保存训练数据
  def fit(self, X, y):
    self.X_train = X # 保存训练特征矩阵
    self.y_train = y # 保存训练目标向量

  # 预测方法，根据最近邻的投票结果，返回预测的目标值
  def predict(self, X):
    y_pred = [] # 存储预测的目标值
    for x in X: # 对每个测试样本
      distances = euclidean_distances(x.reshape(1, -1), self.X_train) # 计算测试样本与训练样本的欧氏距离
      indices = np.argsort(distances) # 对距离进行升序排序，得到索引
      neighbors = self.y_train[indices[0, :self.n_neighbors]] # 根据索引，得到最近邻的目标值
      votes = np.bincount(neighbors) # 对最近邻的目标值进行投票，得到票数
      y_pred.append(np.argmax(votes)) # 根据票数，得到预测的目标值，即票数最多的类别
    return np.array(y_pred) # 返回预测的目标向量

# 创建一个最近邻分类器的实例，设置最近邻的个数为3
model = NearestNeighborClassifier(n_neighbors=3)

# 使用数据点来训练模型
model.fit(X, y)

# 预测新的数据点的目标值
X_new = np.array([[5.1, 3.5, 1.4, 0.2], [6.7, 3.1, 4.4, 1.4], [6.3, 3.3, 6.0, 2.5]]) # 新的特征矩阵，包含三个新的样本
y_pred = model.predict(X_new) # 预测的目标向量，包含三个预测的目标值
print(y_pred)

# 绘制数据点和预测的结果
plt.figure(figsize=(10, 10)) # 设置图像的大小
plt.scatter(X[y==0, 0], X[y==0, 1], color="blue", label="Class 0") # 绘制类别为0的数据点
plt.scatter(X[y==1, 0], X[y==1, 1], color="red", label="Class 1") # 绘制类别为1的数据点
plt.scatter(X[y==2, 0], X[y==2, 1], color="green", label="Class 2") # 绘制类别为2的数据点
plt.scatter(X_new[:, 0], X_new[:, 1], color="black", marker="x", label="New samples") # 绘制新的样本点
plt.xlabel("x1") # 设置x轴的标签
plt.ylabel("x2") # 设置y轴的标签
plt.legend() # 显示图例
plt.show() # 显示图像
