# 导入必要的库
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 创建一些示例数据
# x为特征，y为目标变量
x = np.array([[1], [2], [3], [4], [5]])
y = np.array([1, 2, 4, 7, 11])

# 将数据集分为训练集和测试集
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# 创建线性回归模型
model = LinearRegression()

# 用训练集数据训练模型
model.fit(x_train, y_train)

# 使用测试集进行预测
y_pred = model.predict(x_test)

# 计算并打印均方误差
mse = mean_squared_error(y_test, y_pred)
print(f"均方误差为: {mse}")

# 打印模型参数
print(f"模型的斜率为: {model.coef_}")
print(f"模型的截距为: {model.intercept_}")

# 使用模型进行预测
new_data = np.array([[6]])
prediction = model.predict(new_data)
print(f"当x为6时，预测的y值为: {prediction}")
