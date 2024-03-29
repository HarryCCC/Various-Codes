'''

写代码：个股在过去特定时间段（例：过去28天）内的股价涨跌表现（记作X)，
与不同股票（股票1,2,3...)在不同历史时间段（即同样为28天的数据日期范围内的任意时间段1,2,3...）的涨跌表现（记作Y）。
我们尝试找到最接近的X和Y。
方法是：将Y的每个时间点（每天）的涨跌幅与X的对应每天的涨跌幅数据，采用欧几里得距离的方法进行处理，从而得到最拟合X的前10组Y。

这里，共有五千余支股票，几百天，X就是每支个股的最后28个有效时间序列数据（共有五千余个X），
Y就是对于每支股票的全周期数据的任意28天区间的序列数据（共有五千余乘几百等于约几百万个Y）。

再对1个fitted stock的28个数据点的数据序列（X）
与10个matched stock 1,2,3...的56个数据点的数据序列（Y以及Y之后的28个数据点），同时可视化在同一张图像上。
matched stock的前28个数据点用于拟合fitted stock，后28个数据点序列是真实的日期递推，用于观测之后28天的涨跌幅可能。

控制台实时展示计算进度。

'''

import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestRegressor

# 读取数据
def read_data(file_path):
    try:
        # 读取股票代码和名称
        df_codes_names = pd.read_excel(file_path, skiprows=2, header=None, usecols=[0, 1])
        stock_codes = df_codes_names.iloc[:, 0].values
        stock_names = df_codes_names.iloc[:, 1].values
        # 读取股价数据
        # 加载数据，跳过前2行和前2列
        df_prices = pd.read_excel(file_path, skiprows=2, header=None, usecols=lambda column: column not in [0, 1])
        # 删除全零列 
        df_prices = df_prices.loc[:, (df_prices != 0).any(axis=0)] 
        # 反转序列数据
        df_prices = df_prices.apply(lambda row: row[::-1], axis=1)
        
        return df_prices, stock_codes, stock_names
    except Exception as e:
        print(f"An error occurred while reading the data: {e}")
        return None, None, None
    
# 寻找最接近的Y
def find_closest_y(X, Y):
    # 使用NearestNeighbors来找到最近的10个邻居
    nbrs = NearestNeighbors(n_neighbors=10, algorithm='ball_tree').fit(Y)
    distances, indices = nbrs.kneighbors([X])
    return indices[0]

# 可视化数据
def visualize_data(fitted_stock, matched_stocks_indices, Y, Y_followup):
    # 创建两个子图
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    # 在左侧图像上绘制fitted_stock和match_stock的前28天数据
    axs[0].plot(fitted_stock, label="Fitted Stock", alpha=1.0)  # 设置拟合股票的透明度为完全不透明
    for i, index in enumerate(matched_stocks_indices):
        matched_stock_initial = Y[index]
        axs[0].plot(matched_stock_initial, label=f"Matched Stock {i+1} (Initial)", alpha=0.5)  # 设置匹配股票的透明度为50%
    axs[0].legend()
    axs[0].set_title('Initial 28 Days')

    # 在右侧图像上绘制match_stock的后续28天数据
    for i, index in enumerate(matched_stocks_indices):
        matched_stock_followup = Y_followup[index]
        axs[1].plot(matched_stock_followup, label=f"Matched Stock {i+1} (Follow-up)", linestyle='--', alpha=0.5)  # 设置匹配股票的透明度为50%

    # 使用随机森林回归进行非线性拟合
    X_fit = np.array(range(28)).reshape(-1, 1)  # 用于拟合的x坐标
    y_fit = np.mean(Y_followup, axis=0)  # 计算拟合曲线的y坐标（取平均值）
    rf = RandomForestRegressor(n_estimators=100, random_state=42)  # 创建随机森林回归模型
    rf.fit(X_fit, y_fit)
    y_rf = rf.predict(X_fit)  # 使用随机森林模型进行预测
    axs[1].plot(X_fit, y_rf, 'k-', label='Fitted Trend', alpha=1.0)  # 绘制拟合曲线，黑色实线，完全不透明
    axs[1].legend()
    axs[1].set_title('Follow-up 28 Days Fitted Trend with Random Forest')
    # 显示图像
    plt.tight_layout()
    plt.show()

# 主函数
def main():
    file_path = "stock_data.xlsx"
    df_prices, stock_codes, stock_names = read_data(file_path)
    if df_prices is not None:
        # 创建一个进度条
        pbar = tqdm(total=len(stock_codes), ascii=True)
        for i, (stock_code, stock_name) in enumerate(zip(stock_codes, stock_names)):
            # 获取当前股票的数据
            current_stock_data = df_prices.iloc[i].values
            # 切割数据为X和Y
            X = current_stock_data[-28:]
            Y = [current_stock_data[j:j+28] for j in range(len(current_stock_data) - 56)]  # 减少Y的长度，以便包含后续28天数据
            Y_followup = [current_stock_data[j+28:j+56] for j in range(len(current_stock_data) - 56)]  # 获取Y的后续28天数据
            # 寻找最接近的Y
            closest_y_indices = find_closest_y(X, Y)
            # 可视化数据
            # visualize_data(X, closest_y_indices, Y, Y_followup)
            # 更新进度条
            pbar.update(1)
        pbar.close()
        
if __name__ == "__main__":
    main()
