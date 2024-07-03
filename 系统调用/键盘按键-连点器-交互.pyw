import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui

# 定义自动按键类
class AutoKeyPress:
    def __init__(self, key='1', interval=1.0):
        self.key = key
        self.interval = interval
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def run(self):
        while self.running:
            pyautogui.press(self.key)
            time.sleep(self.interval)

# 创建Tkinter窗口
class AutoKeyPressApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自动按键程序")

        self.key_var = tk.StringVar(value='1')
        self.interval_var = tk.DoubleVar(value=1.0)
        self.autokey = AutoKeyPress()

        self.create_widgets()

    def create_widgets(self):
        # 按键设置
        ttk.Label(self.root, text="按键:").grid(column=0, row=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.key_var, width=10).grid(column=1, row=0, padx=10, pady=10)

        # 时间间隔设置
        ttk.Label(self.root, text="时间间隔(秒):").grid(column=0, row=1, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.interval_var, width=10).grid(column=1, row=1, padx=10, pady=10)

        # 启动按钮
        self.start_button = ttk.Button(self.root, text="启动", command=self.start_autokey)
        self.start_button.grid(column=0, row=2, padx=10, pady=10)

        # 停止按钮
        self.stop_button = ttk.Button(self.root, text="停止", command=self.stop_autokey, state=tk.DISABLED)
        self.stop_button.grid(column=1, row=2, padx=10, pady=10)

    def start_autokey(self):
        key = self.key_var.get()
        interval = self.interval_var.get()
        self.autokey = AutoKeyPress(key, interval)
        self.autokey.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_autokey(self):
        self.autokey.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoKeyPressApp(root)
    root.mainloop()
