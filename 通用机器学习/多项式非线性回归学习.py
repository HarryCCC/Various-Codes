# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 创建一些具有曲率的示例数据
x = np.linspace(0, 10, 100)
y = np.sin(x) + np.random.normal(0, 0.5, 100)  # 加入一些噪声

# 将数据集分为训练集和测试集
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

# 创建多项式回归模型，这里我们使用二次多项式
degree = 3
polynomial_regression = make_pipeline(PolynomialFeatures(degree), LinearRegression())

# 用训练集数据训练模型
polynomial_regression.fit(x_train[:, np.newaxis], y_train)

# 使用测试集进行预测
y_pred = polynomial_regression.predict(x_test[:, np.newaxis])

# 计算并打印测试集的均方误差（测试损失）
test_loss = mean_squared_error(y_test, y_pred)
print(f"测试集的均方误差（测试损失）为: {test_loss}")

# 输出拟合出的多项式系数
coefficients = polynomial_regression.named_steps['linearregression'].coef_
# 构造多项式的字符串表示
polynomial_str = ""
for i, coef in enumerate(reversed(coefficients)):
    if i == 0:
        polynomial_str = f"{coef:.2f}x^{degree-i}" + polynomial_str
    else:
        polynomial_str = f" + {coef:.2f}x^{degree-i}" + polynomial_str

print(f"拟合出的多项式为: {polynomial_str}")


# 绘制数据点和拟合曲线
x_plot = np.linspace(0, 10, 1000)
y_plot = polynomial_regression.predict(x_plot[:, np.newaxis])

plt.scatter(x_train, y_train, color='black', label='Training data')
plt.scatter(x_test, y_test, color='red', label='Test data')
plt.plot(x_plot, y_plot, color='blue', label='Polynomial fit')
plt.legend()
plt.show()
