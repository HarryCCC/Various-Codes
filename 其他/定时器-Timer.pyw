import tkinter as tk

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry('+0+0')  # 窗口紧贴在屏幕的左上角
        self.master.attributes('-topmost', True)  # 窗口始终悬浮在最前面
        self.master.configure(bg='black')  # 设置背景颜色为黑色
        self.master.overrideredirect(True)  # 移除窗口边框

        # 添加一个可以拖动的区域
        self.draggable_area = tk.Frame(self.master, bg='black', height=30)
        self.draggable_area.pack(fill='x')
        self.draggable_area.bind('<ButtonPress-1>', self.start_move)
        self.draggable_area.bind('<ButtonRelease-1>', self.stop_move)
        self.draggable_area.bind('<B1-Motion>', self.do_move)

        self.timer = '00:10:00'  # 先定义self.timer
        self.counting = False

        # 添加自定义的最小化、最大化和关闭按钮
        self.button_frame = tk.Frame(self.master, bg='black')
        self.button_frame.pack(anchor='ne')

        self.minimize_button = tk.Button(self.button_frame, text="-", command=self.minimize, fg='white', bg='black')
        self.minimize_button.pack(side='left')

        self.maximize_button = tk.Button(self.button_frame, text="□", command=self.maximize, fg='white', bg='black')
        self.maximize_button.pack(side='left')

        self.close_button = tk.Button(self.button_frame, text="x", command=self.master.destroy, fg='white', bg='black')
        self.close_button.pack(side='left')

        # 启动页面
        self.start_frame = tk.Frame(self.master, bg='black')
        self.start_frame.pack(expand=True)

        self.time_frame = tk.Frame(self.start_frame, bg='black')
        self.time_frame.pack(pady=20, padx=50)  # 在左右侧各添加50像素的空白区域

        self.hh_entry = tk.Entry(self.time_frame, width=5, font=("Helvetica", 18), fg='white', bg='black')
        self.hh_entry.insert(0, '00')
        self.hh_entry.pack(side='left')

        tk.Label(self.time_frame, text="h", font=("Helvetica", 18), fg='white', bg='black').pack(side='left')

        self.mm_entry = tk.Entry(self.time_frame, width=5, font=("Helvetica", 18), fg='white', bg='black')
        self.mm_entry.insert(0, '10')
        self.mm_entry.pack(side='left')

        tk.Label(self.time_frame, text="m", font=("Helvetica", 18), fg='white', bg='black').pack(side='left')

        self.ss_entry = tk.Entry(self.time_frame, width=5, font=("Helvetica", 18), fg='white', bg='black')
        self.ss_entry.insert(0, '00')
        self.ss_entry.pack(side='left')

        tk.Label(self.time_frame, text="s", font=("Helvetica", 18), fg='white', bg='black').pack(side='left')

        self.start_button = tk.Button(self.start_frame, text="Start", command=self.start_timer, fg='white', bg='black')
        self.start_button.pack(pady=20)

        # 倒计时页面
        self.countdown_frame = tk.Frame(self.master, bg='black')
        self.countdown_label = tk.Label(self.countdown_frame, text=self.timer, font=("Helvetica", 48), fg='white', bg='black')
        self.countdown_label.pack(pady=50, padx=50)  # 在上下左右各添加50像素的空白区域

        self.forgo_button = tk.Button(self.countdown_frame, text="Forgo", command=self.forgo, fg='white', bg='black')
        self.forgo_button.pack(pady=30)

        # 结束页面
        self.end_frame = tk.Frame(self.master, bg='black')

        self.end_label = tk.Label(self.end_frame, text=" 感谢你伟大的努力，自律使你愈加自由！\n--- from the future self", font=("Helvetica", 20), fg='white', bg='black')
        self.end_label.pack(pady=20)

        self.restart_button = tk.Button(self.end_frame, text="Restart", command=self.restart, fg='white', bg='black')
        self.restart_button.pack(pady=20)

    def start_timer(self):
        self.timer = f"{self.hh_entry.get().zfill(2)}:{self.mm_entry.get().zfill(2)}:{self.ss_entry.get().zfill(2)}"
        self.start_frame.pack_forget()
        self.countdown_frame.pack(expand=True)
        self.countdown_label.pack(pady=20)
        self.counting = True
        self.countdown()

    def countdown(self):
        if self.counting:
            hh, mm, ss = map(int, self.timer.split(':'))
            if ss > 0:
                ss -= 1
            elif mm > 0:
                mm -= 1
                ss = 59
            elif hh > 0:
                hh -= 1
                mm = 59
                ss = 59
            else:
                self.counting = False
                self.countdown_frame.pack_forget()
                self.end_frame.pack(expand=True)
                self.end_label.pack(pady=20)
                self.restart_button.pack()

            self.timer = f"{hh:02d}:{mm:02d}:{ss:02d}"
            self.countdown_label.config(text=self.timer)
            self.master.after(1000, self.countdown)

    def restart(self):
        self.end_frame.pack_forget()
        self.start_frame.pack(expand=True)

    def minimize(self):
        self.master.overrideredirect(False)
        self.master.iconify()

    def maximize(self):
        if self.master.state() == 'zoomed':
            self.master.state('normal')
        else:
            self.master.state('zoomed')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        dx = event.x - self.x
        dy = event.y - self.y
        x = self.master.winfo_x() + dx
        y = self.master.winfo_y() + dy
        self.master.geometry(f"+{x}+{y}")
    
    def forgo(self):
        self.counting = False
        self.countdown_frame.pack_forget()
        self.start_frame.pack(expand=True)

root = tk.Tk()
app = TimerApp(root)
root.mainloop()
