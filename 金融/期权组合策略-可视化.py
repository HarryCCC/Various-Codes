import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 解决中文显示问题
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 定义期权类
class Option:
    def __init__(self, type_, strike, price, quantity=1):
        self.type = type_  # "call" 或 "put"
        self.strike = strike  # 行权价
        self.price = price  # 期权费
        self.quantity = quantity  # 期权合约数

    def payoff(self, S):
        if self.type == 'call':
            return np.maximum(S - self.strike, 0) * self.quantity - self.price * self.quantity
        elif self.type == 'put':
            return np.maximum(self.strike - S, 0) * self.quantity - self.price * self.quantity

def calculate_strategy_payoff(options, stock_prices):
    total_payoff = np.zeros_like(stock_prices)
    for option in options:
        total_payoff += option.payoff(stock_prices)
    return total_payoff

# GUI应用类
class OptionVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("期权组合策略可视化")
        
        # 默认期权设置
        self.options = [Option('call', 100, 10) for _ in range(5)]
        
        # 创建GUI元素
        self.create_widgets()

    def create_widgets(self):
        # ====== 标题 ====== #
        title = tk.Label(self.root, text="期权组合策略可视化", font=("Arial", 16))
        title.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")

        # ====== 左侧参数输入区域 ====== #
        self.param_frame = tk.Frame(self.root)
        self.param_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # 让左侧列在水平方向也能自适应
        self.root.grid_columnconfigure(0, weight=1)
        # 让右侧列在水平方向也能自适应（显示图表那一列）
        self.root.grid_columnconfigure(1, weight=2)

        # 让 row=1 这一行在垂直方向也可自适应
        self.root.grid_rowconfigure(1, weight=1)

        # 在左侧的 param_frame 中创建 5 行期权输入
        for i in range(5):
            tk.Label(self.param_frame, text=f"期权{i+1}类型:").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            tk.Label(self.param_frame, text=f"行权价:").grid(row=i, column=2, padx=5, pady=5, sticky="e")
            tk.Label(self.param_frame, text=f"期权价格:").grid(row=i, column=4, padx=5, pady=5, sticky="e")

            option_type = ttk.Combobox(self.param_frame, values=["call", "put"], state="readonly")
            option_type.set(self.options[i].type)
            option_type.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

            option_strike = tk.Entry(self.param_frame)
            option_strike.insert(0, str(self.options[i].strike))
            option_strike.grid(row=i, column=3, padx=5, pady=5, sticky="ew")

            option_price = tk.Entry(self.param_frame)
            option_price.insert(0, str(self.options[i].price))
            option_price.grid(row=i, column=5, padx=5, pady=5, sticky="ew")

            setattr(self, f"option{i+1}_type", option_type)
            setattr(self, f"option{i+1}_strike", option_strike)
            setattr(self, f"option{i+1}_price", option_price)

        # ====== 策略按钮区域，使用多行布局（模拟换行） ====== #
        # 这里设定“4列布局”，超过4个按钮自动从下一行开始
        self.strategy_frame = tk.Frame(self.root)
        self.strategy_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        strategies = [
            "牛市价差", "熊市价差", "蝶式", "铁鹰式", 
            "牛市看跌价差", "保护性看跌期权", "裸卖空", "铁式蝶式"
        ]

        # 多列布局：假设4列按钮，超出后换行
        columns_per_row = 4
        for idx, strategy in enumerate(strategies):
            row = idx // columns_per_row
            col = idx % columns_per_row
            btn = tk.Button(self.strategy_frame, text=strategy, command=lambda s=strategy: self.set_strategy(s))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # 让按钮所在 frame 的每一列都能自适应
        for col_idx in range(columns_per_row):
            self.strategy_frame.columnconfigure(col_idx, weight=1)

        # ====== 可视化按钮 ====== #
        self.visualize_button = tk.Button(self.root, text="可视化", command=self.visualize)
        self.visualize_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

    # ==================== 设置策略的函数 ==================== #
    def set_strategy(self, strategy):
        if strategy == "牛市价差":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "100")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "5")
            
            self.option2_type.set("call")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "110")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "3")
            
            for i in range(2, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "熊市价差":
            self.option1_type.set("put")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "120")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "6")
            
            self.option2_type.set("put")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "110")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "3")
            
            for i in range(2, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "蝶式":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "100")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "5")
            
            self.option2_type.set("call")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "110")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "8")
            
            self.option3_type.set("call")
            self.option3_strike.delete(0, tk.END)
            self.option3_strike.insert(0, "120")
            self.option3_price.delete(0, tk.END)
            self.option3_price.insert(0, "5")
            
            for i in range(3, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "铁鹰式":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "90")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "4")
            
            self.option2_type.set("put")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "100")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "5")
            
            self.option3_type.set("put")
            self.option3_strike.delete(0, tk.END)
            self.option3_strike.insert(0, "110")
            self.option3_price.delete(0, tk.END)
            self.option3_price.insert(0, "4")
            
            self.option4_type.set("call")
            self.option4_strike.delete(0, tk.END)
            self.option4_strike.insert(0, "120")
            self.option4_price.delete(0, tk.END)
            self.option4_price.insert(0, "3")

            for i in range(4, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "牛市看跌价差":
            self.option1_type.set("put")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "120")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "7")
            
            self.option2_type.set("put")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "130")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "3")
            
            for i in range(2, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "保护性看跌期权":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "100")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "10")
            
            self.option2_type.set("put")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "95")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "3")
            
            for i in range(2, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "裸卖空":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "100")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "5")
            
            for i in range(1, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

        elif strategy == "铁式蝶式":
            self.option1_type.set("call")
            self.option1_strike.delete(0, tk.END)
            self.option1_strike.insert(0, "100")
            self.option1_price.delete(0, tk.END)
            self.option1_price.insert(0, "6")
            
            self.option2_type.set("put")
            self.option2_strike.delete(0, tk.END)
            self.option2_strike.insert(0, "110")
            self.option2_price.delete(0, tk.END)
            self.option2_price.insert(0, "5")
            
            self.option3_type.set("call")
            self.option3_strike.delete(0, tk.END)
            self.option3_strike.insert(0, "120")
            self.option3_price.delete(0, tk.END)
            self.option3_price.insert(0, "4")
            
            self.option4_type.set("put")
            self.option4_strike.delete(0, tk.END)
            self.option4_strike.insert(0, "130")
            self.option4_price.delete(0, tk.END)
            self.option4_price.insert(0, "2")

            for i in range(4, 5):
                getattr(self, f"option{i+1}_type").set("")
                getattr(self, f"option{i+1}_strike").delete(0, tk.END)
                getattr(self, f"option{i+1}_price").delete(0, tk.END)

    # ==================== 可视化函数 ==================== #
    def visualize(self):
        # 获取输入的期权参数
        stock_prices = np.linspace(50, 150, 500)
        options = []
        for i in range(5):
            type_ = getattr(self, f"option{i+1}_type").get()
            strike = getattr(self, f"option{i+1}_strike").get().strip()
            price = getattr(self, f"option{i+1}_price").get().strip()

            if strike == "":
                strike = "100"
            if price == "":
                price = "10"

            try:
                strike = float(strike)
                price = float(price)
            except ValueError:
                print(f"期权{i+1}的参数无效，跳过此期权")
                continue

            if type_:
                options.append(Option(type_, strike, price))

        if not options:
            print("没有有效的期权输入")
            return

        # 计算期权组合策略的收益
        payoff = calculate_strategy_payoff(options, stock_prices)

        # 绘制图像
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(stock_prices, payoff, label="组合策略")
        ax.axhline(0, color="black", linewidth=1)
        ax.set_xlabel("标的资产价格")
        ax.set_ylabel("收益")
        ax.set_title("期权组合策略收益图")
        ax.legend()

        # 在Tkinter窗口中显示Matplotlib图像
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=6, padx=5, pady=5, sticky="nsew")
        canvas.draw()


# 程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = OptionVisualizerApp(root)
    root.mainloop()
