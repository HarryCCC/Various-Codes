# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans

# 生成一些随机的数据点
X, y = make_blobs(n_samples=200, n_features=2, centers=3, cluster_std=0.5, random_state=0) # 特征矩阵和目标向量，每个样本有两个特征，共有三个类别

# 创建一个K均值聚类的实例，设置聚类的个数为3
model = KMeans(n_clusters=3)

# 使用数据点来训练模型
model.fit(X)

# 预测新的数据点的类别
X_new = np.array([[0, 4], [4, 0], [-4, -4]]) # 新的特征矩阵，包含三个新的样本
y_pred = model.predict(X_new) # 预测的目标向量，包含三个预测的类别
print(y_pred)

# 绘制数据点和聚类的结果
plt.figure(figsize=(10, 10)) # 设置图像的大小
plt.scatter(X[:, 0], X[:, 1], c=model.labels_, cmap="rainbow") # 绘制数据点，根据模型的标签来分配颜色
plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], color="black", marker="x", label="Centroids") # 绘制聚类的中心点
plt.scatter(X_new[:, 0], X_new[:, 1], color="white", marker="o", label="New samples") # 绘制新的样本点
plt.xlabel("x1") # 设置x轴的标签
plt.ylabel("x2") # 设置y轴的标签
plt.legend() # 显示图例
plt.show() # 显示图像
