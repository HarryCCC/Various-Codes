import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
from pynput import mouse
import time

# 全局变量，用于控制滚动状态
scrolling = False
stop_event = threading.Event()
scroll_speed = 30  # 默认滚动速度

def on_click(x, y, button, pressed):
    if pressed:
        # 当检测到鼠标单击时，停止滚动
        stop_event.set()
        return False  # 停止监听

def scroll_up_continuous():
    with mouse.Listener(on_click=on_click) as listener:
        while not stop_event.is_set():
            pyautogui.scroll(scroll_speed)  # 使用实时设定的滚动速度
            time.sleep(0.00001)  # 减小时间间隔，增加频率
        listener.join()
    global scrolling
    scrolling = False  # 重置滚动状态

def scroll_down_continuous():
    with mouse.Listener(on_click=on_click) as listener:
        while not stop_event.is_set():
            pyautogui.scroll(-scroll_speed)  # 使用实时设定的滚动速度
            time.sleep(0.00001)  # 减小时间间隔，增加频率
        listener.join()
    global scrolling
    scrolling = False  # 重置滚动状态

def start_scroll_up():
    global scrolling
    if not scrolling:
        scrolling = True
        stop_event.clear()
        t = threading.Thread(target=scroll_up_continuous)
        t.start()
        root.iconify()  # 最小化窗口

def start_scroll_down():
    global scrolling
    if not scrolling:
        scrolling = True
        stop_event.clear()
        t = threading.Thread(target=scroll_down_continuous)
        t.start()
        root.iconify()  # 最小化窗口

def set_speed(*args):
    global scroll_speed
    try:
        scroll_speed = int(speed_var.get())
    except ValueError:
        scroll_speed = 20  # 如果输入无效，设置默认值20

# 创建主窗口
root = tk.Tk()
root.title("滑动模拟器")
root.geometry("300x250")  # 调整窗口大小
root.configure(bg="#2E2E2E")  # 设置灰黑色背景

# 使用 ttk 风格
style = ttk.Style()
style.theme_use('clam')  # 选择主题，可以尝试 'clam', 'alt', 'default', 'classic'
style.configure('TButton', font=('Helvetica', 12), padding=6)
style.configure('TButton', background='#4F4F4F', foreground='white')
style.map('TButton',
          foreground=[('active', 'white')],
          background=[('active', '#6E6E6E')])

# 创建容器框架
frame = ttk.Frame(root, padding=20, style='TFrame')
frame.pack(expand=True)

# 创建“向上滑动”按钮
btn_up = ttk.Button(frame, text="向上滑动", command=start_scroll_up, style='TButton')
btn_up.pack(pady=10, fill='x')

# 创建“向下滑动”按钮
btn_down = ttk.Button(frame, text="向下滑动", command=start_scroll_down, style='TButton')
btn_down.pack(pady=10, fill='x')

# 创建速度设定输入框
speed_label = ttk.Label(frame, text="速度设定：", style='TButton')
speed_label.pack(pady=5)
speed_var = tk.StringVar(value=str(scroll_speed))
speed_entry = ttk.Entry(frame, textvariable=speed_var, font=('Helvetica', 12))
speed_entry.pack(pady=5, fill='x')
speed_var.trace_add("write", set_speed)  # 绑定实时更新速度的回调函数

# 运行主循环
root.mainloop()
