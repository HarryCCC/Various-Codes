# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 生成一些随机的数据点
X = np.random.rand(100, 1) # 特征矩阵，每个样本只有一个特征
y = 3 * X + 2 + np.random.randn(100, 1) # 目标向量，每个样本只有一个目标值，加上一些噪声

# 创建一个线性回归模型的实例
model = LinearRegression()

# 使用数据点来训练模型
model.fit(X, y)

# 预测新的数据点的目标值
X_new = np.array([[0], [1]]) # 新的特征矩阵，包含两个新的样本
y_pred = model.predict(X_new) # 预测的目标向量，包含两个预测的目标值

# 打印模型的参数
print("模型的斜率：", model.coef_) # 模型的斜率，也就是权重向量
print("模型的截距：", model.intercept_) # 模型的截距，也就是偏置项

# 绘制数据点和模型的直线
plt.scatter(X, y, color="blue") # 绘制数据点
plt.plot(X_new, y_pred, color="red") # 绘制模型的直线
plt.xlabel("x") # 设置x轴的标签
plt.ylabel("y") # 设置y轴的标签
plt.show() # 显示图像
