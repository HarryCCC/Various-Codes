import tkinter as tk
import pyautogui  # 使用pyautogui库来模拟鼠标和键盘操作
import time

class Clicker:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("连点器")
        self.window.geometry("+{}+{}".format(int(self.window.winfo_screenwidth()/2-150), int(self.window.winfo_screenheight()/2-100)))
        
        self.window.minsize(300, 200)
        self.window.maxsize(500, 400)

        self.mouse_status = tk.StringVar()
        self.mouse_status.set("鼠标状态：未运行")
        self.space_status = tk.StringVar()
        self.space_status.set("空格状态：未运行")
        self.mouse_speed = tk.StringVar()
        self.mouse_speed.set("2")
        self.space_speed = tk.StringVar()
        self.space_speed.set("2")
        self.mouse_clicking = False
        self.space_clicking = False
        self.create_widgets()
        
        self.window.mainloop()

    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(expand=True)
        
        # 鼠标操作区
        mouse_frame = tk.Frame(frame)
        mouse_frame.pack(side=tk.LEFT, expand=True)
        mouse_status_label = tk.Label(mouse_frame, textvariable=self.mouse_status)
        mouse_status_label.pack()
        mouse_start_button = tk.Button(mouse_frame, text="开始", command=self.start_mouse_clicking)
        mouse_start_button.pack()
        mouse_stop_button = tk.Button(mouse_frame, text="停止", command=self.stop_mouse_clicking)
        mouse_stop_button.pack()
        mouse_speed_label = tk.Label(mouse_frame, text="点击速度（秒）:")
        mouse_speed_label.pack()
        mouse_speed_entry = tk.Entry(mouse_frame, textvariable=self.mouse_speed)
        mouse_speed_entry.pack()
        
        # 空格操作区
        space_frame = tk.Frame(frame)
        space_frame.pack(side=tk.RIGHT, expand=True)
        space_status_label = tk.Label(space_frame, textvariable=self.space_status)
        space_status_label.pack()
        space_start_button = tk.Button(space_frame, text="开始", command=self.start_space_clicking)
        space_start_button.pack()
        space_stop_button = tk.Button(space_frame, text="停止", command=self.stop_space_clicking)
        space_stop_button.pack()
        space_speed_label = tk.Label(space_frame, text="点击速度（秒）:")
        space_speed_label.pack()
        space_speed_entry = tk.Entry(space_frame, textvariable=self.space_speed)
        space_speed_entry.pack()

    def start_mouse_clicking(self):
        if not self.mouse_clicking:
            self.mouse_clicking = True
            self.mouse_status.set("鼠标状态：运行中")
            self.mouse_click()

    def stop_mouse_clicking(self):
        self.mouse_clicking = False
        self.mouse_status.set("鼠标状态：未运行")

    def mouse_click(self):
        if self.mouse_clicking:
            pyautogui.click()  # 使用pyautogui库来模拟鼠标左键单击
            print("鼠标已单击")  # 监视代码
            delay = int(float(self.mouse_speed.get()) * 1000)
            self.window.after(delay, self.mouse_click)


    def start_space_clicking(self):
        if not self.space_clicking:
            self.space_clicking = True
            self.space_status.set("空格状态：运行中")
            self.space_click()

    def stop_space_clicking(self):
        self.space_clicking = False
        self.space_status.set("空格状态：未运行")

    def space_click(self):
        if self.space_clicking:
            pyautogui.press('space')  # 使用pyautogui库来模拟空格键单击
            print("空格键已单击")  # 监视代码
            delay = int(float(self.space_speed.get()) * 1000)
            self.window.after(delay, self.space_click)

if __name__ == "__main__":
    Clicker()
