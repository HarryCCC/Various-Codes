# -*- coding: utf-8 -*-

"""
高级图片播放器
版本 5.2 (最终版):
- 程序启动时默认显示主窗口，不再默认隐藏。
- 将自定义标题栏的关闭按钮图标恢复为'✕'。
- 程序通过右下角系统托盘图标进行管理，不在任务栏显示。
- 回归完全无边框设计，提供纯粹的沉浸式体验。
"""

import tkinter as tk
from tkinter import messagebox
import os
import random
from PIL import Image, ImageTk, ImageOps, ImageFilter
import sys
import ctypes
import threading
from pystray import MenuItem as item, Icon

# --- 全局参数 ---
TIME_INTERVAL_SECONDS = 2
SUPPORTED_EXTENSIONS = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')
BLUR_RADIUS = 10 

# --- HEIF/HEIC格式支持 ---
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

# --- 主程序类 ---
class AdvancedImagePlayer:
    TITLE_BAR_HOVER_HEIGHT = 40

    def __init__(self, root, image_files, initial_geometry):
        self.root = root
        self.image_files = image_files
        self.current_index = -1
        self.after_id = None
        self.resize_job = None

        self.is_fullscreen = False
        self.is_pinned = True 
        self.windowed_geometry = initial_geometry
        self._drag_data = {"x": 0, "y": 0}

        self.root.title("图片播放器")
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        self.root.geometry(self.windowed_geometry)
        self.root.attributes('-topmost', self.is_pinned)

        self.background_label = tk.Label(self.root, bg='black')
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.image_label = tk.Label(self.root)
        self.image_label.place(in_=self.background_label, anchor="center", relx=0.5, rely=0.5)
        
        self.create_custom_title_bar()
        self.pin_button.config(fg='cyan') 
        
        self.grip_br = tk.Frame(self.root, cursor="bottom_right_corner")
        self.grip_br.place(relx=1.0, rely=1.0, anchor='se', width=15, height=15)
        self.grip_br.bind("<B1-Motion>", self.on_resize_br)

        self.grip_bl = tk.Frame(self.root, cursor="bottom_left_corner")
        self.grip_bl.place(relx=0.0, rely=1.0, anchor='sw', width=15, height=15)
        self.grip_bl.bind("<B1-Motion>", self.on_resize_bl)

        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<Configure>", self.on_configure)
        self.image_label.bind("<Button-1>", self.manual_next_image)

        self.root.after(50, self.start_application)

    def start_application(self):
        self.show_next_image()
        self.manage_title_bar_visibility()

    def on_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            self.root.withdraw()

    def on_resize_br(self, event):
        if not self.is_fullscreen:
            new_width = self.root.winfo_width() + event.x
            new_height = self.root.winfo_height() + event.y
            self.root.geometry(f"{new_width}x{new_height}")

    def on_resize_bl(self, event):
        if not self.is_fullscreen:
            dx = event.x
            new_width = self.root.winfo_width() - dx
            new_height = self.root.winfo_height() + event.y
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y()
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def on_configure(self, event):
        if not self.is_fullscreen:
            self.windowed_geometry = self.root.geometry()
            if self.resize_job:
                self.root.after_cancel(self.resize_job)
            self.resize_job = self.root.after(150, self.update_image_display)

    def update_image_display(self):
        if self.current_index == -1 or not hasattr(self.image_label, 'current_pil_image'):
            return
        try:
            original_img = self.image_label.current_pil_image.convert("RGB")
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            if win_width <= 1 or win_height <= 1: return

            bg_img = original_img.resize((win_width // 10, win_height // 10), Image.Resampling.BOX)
            bg_img = bg_img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
            bg_img = bg_img.resize((win_width, win_height), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_img)
            self.background_label.config(image=bg_photo)
            self.background_label.image = bg_photo

            img_width, img_height = original_img.size
            scale = min(win_width / img_width, win_height / img_height)
            new_width, new_height = int(img_width * scale), int(img_height * scale)
            if new_width > 0 and new_height > 0:
                resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_img)
                self.image_label.config(image=photo_image, width=new_width, height=new_height)
                self.image_label.image = photo_image
        except Exception as e:
            print(f"更新图片显示时出错: {e}")

    def show_next_image(self):
        if self.root.winfo_width() <= 1 or self.root.winfo_height() <= 1:
            self.after_id = self.root.after(100, self.show_next_image)
            return
        self.current_index = (self.current_index + 1) % len(self.image_files)
        image_path = self.image_files[self.current_index]
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                self.image_label.current_pil_image = img
                self.update_image_display()
        except Exception as e:
            print(f"无法加载图片 '{os.path.basename(image_path)}': {e}")
            self.root.after(100, self.manual_next_image)
            return
        self.after_id = self.root.after(TIME_INTERVAL_SECONDS * 1000, self.show_next_image)
        
    def manage_title_bar_visibility(self):
        try:
            pointer_y = self.root.winfo_pointery()
            win_y = self.root.winfo_y()
            if win_y <= pointer_y < win_y + self.TITLE_BAR_HOVER_HEIGHT:
                self.title_bar.place(x=0, y=0, relwidth=1)
            else:
                title_bar_y = self.title_bar.winfo_y()
                title_bar_height = self.title_bar.winfo_height()
                if pointer_y > title_bar_y + title_bar_height or pointer_y < title_bar_y:
                    self.title_bar.place_forget()
        except tk.TclError:
            pass
        self.root.after(100, self.manage_title_bar_visibility)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.grip_br.place_forget()
            self.grip_bl.place_forget()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.fullscreen_button.config(text='◱')
        else:
            self.grip_br.place(relx=1.0, rely=1.0, anchor='se', width=15, height=15)
            self.grip_bl.place(relx=0.0, rely=1.0, anchor='sw', width=15, height=15)
            self.root.geometry(self.windowed_geometry)
            self.fullscreen_button.config(text='⛶')
        self.root.after(50, self.update_image_display)
    
    def on_close(self, event=None):
        self.root.withdraw()
        
    def manual_next_image(self, event=None):
        if event and event.widget == self.image_label:
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.show_next_image()

    def create_custom_title_bar(self):
        self.title_bar = tk.Frame(self.root, bg='#282828')
        # <--- 修正点 1：将关闭按钮图标改回 '✕' ---
        close_button = tk.Button(self.title_bar, text='✕', bg='#282828', fg='white', relief='flat', command=self.on_close, width=4)
        close_button.pack(side='right')
        self.fullscreen_button = tk.Button(self.title_bar, text='⛶', bg='#282828', fg='white', relief='flat', command=self.toggle_fullscreen, width=4)
        self.fullscreen_button.pack(side='right')
        self.pin_button = tk.Button(self.title_bar, text='📌', bg='#282828', fg='white', relief='flat', command=self.toggle_pin, width=4)
        self.pin_button.pack(side='right')
        drag_handle = tk.Label(self.title_bar, bg='#282828', text="  图片播放器", fg="white")
        drag_handle.pack(side='left', fill='x', expand=True)
        drag_handle.bind("<ButtonPress-1>", self._on_drag_start)
        drag_handle.bind("<B1-Motion>", self._on_drag_motion)

    def toggle_pin(self, event=None):
        self.is_pinned = not self.is_pinned
        self.root.attributes('-topmost', self.is_pinned)
        self.pin_button.config(fg='cyan' if self.is_pinned else 'white')
        
    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

# --- 主函数与智能尺寸计算 ---
def calculate_initial_geometry(image_files: list) -> str:
    try:
        temp_root = tk.Tk()
        temp_root.withdraw()
        screen_width = temp_root.winfo_screenwidth()
        screen_height = temp_root.winfo_screenheight()
        temp_root.destroy()
    except tk.TclError:
        return "400x300"

    max_win_width = screen_width * 0.1
    max_win_height = screen_height * 0.1
    
    target_w, target_h = 0, 0

    for filepath in image_files:
        try:
            with Image.open(filepath) as img:
                img_w, img_h = img.size
                scale = min(max_win_width / img_w, max_win_height / img_h, 1.0)
                scaled_w = img_w * scale
                scaled_h = img_h * scale
                target_w = max(target_w, scaled_w)
                target_h = max(target_h, scaled_h)
        except Exception:
            continue
    
    if target_w < 50 or target_h < 50:
        target_w, target_h = 400, 300

    x_pos = 0
    try:
        class RECT(ctypes.Structure):
            _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                        ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
        rect = RECT()
        ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)
        work_area_bottom = rect.bottom
        y_pos = work_area_bottom - target_h
    except Exception:
        y_pos = screen_height - target_h

    return f"{int(target_w)}x{int(target_h)}+{int(x_pos)}+{int(y_pos)}"

def main():
    try:
        current_directory = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
    except NameError:
        current_directory = os.getcwd()

    image_files = [os.path.join(current_directory, f) for f in os.listdir(current_directory) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    random.shuffle(image_files)

    if not image_files:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("未找到图片", "在当前目录下未找到任何支持的图片文件。")
        root.destroy()
        return

    initial_geometry = calculate_initial_geometry(image_files)

    app_root = tk.Tk()
    # <--- 修正点 2：移除启动时隐藏窗口的这行代码 ---
    # app_root.withdraw() 
    player = AdvancedImagePlayer(app_root, image_files, initial_geometry)

    # --- 系统托盘核心逻辑 ---
    def create_tray_icon():
        try:
            icon_image = Image.open("icon.ico")
        except FileNotFoundError:
            icon_image = Image.new('RGB', (64, 64), 'white')
        
        menu = (
            item('显示/隐藏', on_show_hide, default=True),
            item('切换全屏', on_toggle_fullscreen),
            item('退出', on_exit)
        )
        
        icon = Icon("image_player", icon_image, "图片播放器", menu)
        icon.run()

    def on_show_hide(icon, item):
        if app_root.state() == 'withdrawn':
            app_root.deiconify()
        else:
            app_root.withdraw()

    def on_toggle_fullscreen(icon, item):
        app_root.after(0, player.toggle_fullscreen)

    def on_exit(icon, item):
        icon.stop()
        app_root.destroy()

    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    app_root.mainloop()

if __name__ == "__main__":
    main()