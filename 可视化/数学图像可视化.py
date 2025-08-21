import numpy as np
import matplotlib.pyplot as plt

def plot_functions_v6(*funcs, labels=None):
    # 创建一个颜色列表，用于为每个函数指定不同的颜色
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # 创建一个x值的范围
    x = np.linspace(-10, 10, 400)
    
    y_ranges = []

    # 对于每个传入的函数，都计算其y值的范围
    for i, func in enumerate(funcs):
        try:
            y = [func(val) for val in x]
            y_range = max(y) - min(y)
            y_ranges.append(y_range)
        except:
            print(f"Error plotting function: {func.__name__}")
    
    # 设定一个最小的y轴范围，以确保所有的图像都清晰可见
    min_y_range = min(y_ranges)
    y_min = - min_y_range *2
    y_max = min_y_range *2

    plt.ylim(y_min, y_max)

    # 绘制函数
    for i, func in enumerate(funcs):
        y = [func(val) for val in x]
        label = labels[i] if labels else func.__name__
        plt.plot(x, y, label=label, color=colors[i % len(colors)])

    # 显示图例
    plt.legend()

    # 显示图像
    plt.show()

# 示例函数
def f1(x):
    return x**3

def f2(x):
    return np.sin(x)

def f3(x):
    return np.cos(x)

# 调用绘图函数
plot_functions_v6(f1, f2, f3, labels=['x^3', 'sin(x)', 'cos(x)'])
