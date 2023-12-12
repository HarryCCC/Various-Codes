# 导入tkinter模块，用于创建GUI
import tkinter as tk

# 导入os模块，用于调用系统命令
import os

# 创建一个主窗口对象，设置标题和大小
root = tk.Tk()
root.title("系统功能调用")
root.geometry("300x200")

# 定义打开文件管理器的函数
def open_file_explorer():
    # 使用Windows系统的命令
    os.system("explorer")

# 定义打开计算器的函数
def open_calculator():
    # 使用Windows系统的命令
    os.system("calc")

# 定义打开记事本的函数
def open_notepad():
    # 使用Windows系统的命令
    os.system("notepad")

# 定义打开浏览器的函数
def open_browser():
    # 使用Windows系统的命令
    os.system("start www.bing.com")

# 创建四个按钮对象，分别对应四个功能，并为每个按钮绑定一个事件处理函数
btn_file = tk.Button(root, text="打开文件管理器", command=open_file_explorer)
btn_calc = tk.Button(root, text="打开计算器", command=open_calculator)
btn_note = tk.Button(root, text="打开记事本", command=open_notepad)
btn_brow = tk.Button(root, text="打开浏览器", command=open_browser)

# 使用grid方法，将按钮放置在主窗口中
btn_file.grid(row=0, column=0) # 第一个按钮放在第0行第0列
btn_calc.grid(row=0, column=1) # 第二个按钮放在第0行第1列
btn_note.grid(row=1, column=0) # 第三个按钮放在第1行第0列
btn_brow.grid(row=1, column=1) # 第四个按钮放在第1行第1列

# 设置主窗口的网格配置，使得每一行和每一列都能居中对齐，并且有一定的间距
root.grid_rowconfigure(0, weight=1) # 设置第0行的权重为1，表示该行可以自动调整大小
root.grid_rowconfigure(1, weight=1) # 设置第1行的权重为1，表示该行可以自动调整大小
root.grid_columnconfigure(0, weight=1) # 设置第0列的权重为1，表示该列可以自动调整大小
root.grid_columnconfigure(1, weight=1) # 设置第1列的权重为1，表示该列可以自动调整大小
root.grid_rowconfigure("all", pad=10) # 设置所有行之间的间距为10像素
root.grid_columnconfigure("all", pad=10) # 设置所有列之间的间距为10像素


# 进入主循环，等待用户操作
root.mainloop()
