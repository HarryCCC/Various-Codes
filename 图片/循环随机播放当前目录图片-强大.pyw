# -*- coding: utf-8 -*-

"""
高级图片播放器
版本 3.4 (最终形态版):
- 回归完全无边框设计，在所有模式下提供统一的悬浮标题栏体验。
- 新增左下角和右下角双重拖拽功能，方便手动调节窗口大小。
- 集成所有历史优化，包括ESC分级退出、空格键切换、智能初始尺寸等。
"""

import tkinter as tk
from tkinter import messagebox
import os
import random
from PIL import Image, ImageTk, ImageOps
import sys
from tqdm import tqdm

# --- 全局参数 ---
TIME_INTERVAL_SECONDS = 2
SUPPORTED_EXTENSIONS = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')

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

        # --- 窗口初始化：始终为无边框 ---
        self.root.title("图片播放器")
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        self.root.geometry(self.windowed_geometry)
        self.root.attributes('-topmost', self.is_pinned)

        # --- 核心控件 ---
        self.image_label = tk.Label(self.root, bg='black')
        self.image_label.pack(expand=True, fill='both')
        
        self.create_custom_title_bar()
        self.pin_button.config(fg='cyan') 
        
        # --- 新增：双重拖拽角 ---
        self.grip_br = tk.Frame(self.root, bg='black', cursor="bottom_right_corner")
        self.grip_br.place(relx=1.0, rely=1.0, anchor='se', width=15, height=15)
        self.grip_br.bind("<B1-Motion>", self.on_resize_br)

        self.grip_bl = tk.Frame(self.root, bg='black', cursor="bottom_left_corner")
        self.grip_bl.place(relx=0.0, rely=1.0, anchor='sw', width=15, height=15)
        self.grip_bl.bind("<B1-Motion>", self.on_resize_bl)

        # --- 事件绑定 ---
        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<Configure>", self.on_configure)
        self.root.bind("<space>", self.toggle_fullscreen)
        self.image_label.bind("<Button-1>", self.manual_next_image)

        # --- 启动 ---
        self.root.after(50, self.start_application)

    def start_application(self):
        self.toggle_fullscreen()
        self.show_next_image()
        self.manage_title_bar_visibility()

    def on_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            self.on_close()

    def on_resize_br(self, event):
        """处理右下角拖拽"""
        if not self.is_fullscreen:
            new_width = self.root.winfo_width() + event.x
            new_height = self.root.winfo_height() + event.y
            self.root.geometry(f"{new_width}x{new_height}")

    def on_resize_bl(self, event):
        """处理左下角拖拽"""
        if not self.is_fullscreen:
            dx = event.x
            new_width = self.root.winfo_width() - dx
            new_height = self.root.winfo_height() + event.y
            
            # 同时移动窗口位置以保持左上角不动
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y()
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

    def on_configure(self, event):
        if not self.is_fullscreen:
            self.windowed_geometry = self.root.geometry()
            if self.resize_job:
                self.root.after_cancel(self.resize_job)
            self.resize_job = self.root.after(150, self.redraw_current_image)

    def redraw_current_image(self):
        if self.current_index == -1 or not hasattr(self.image_label, 'current_pil_image'):
            return
        try:
            img = self.image_label.current_pil_image
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            if win_width <= 1 or win_height <= 1: return
            img_width, img_height = img.size
            scale = min(win_width / img_width, win_height / img_height)
            new_width, new_height = int(img_width * scale), int(img_height * scale)
            if new_width > 0 and new_height > 0:
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo_image = ImageTk.PhotoImage(resized_img)
                self.image_label.config(image=photo_image)
                self.image_label.image = photo_image
        except Exception as e:
            print(f"重绘图片时出错: {e}")

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
                self.redraw_current_image()
        except Exception as e:
            print(f"无法加载图片 '{os.path.basename(image_path)}': {e}")
            self.root.after(100, self.manual_next_image)
            return
        self.after_id = self.root.after(TIME_INTERVAL_SECONDS * 1000, self.show_next_image)
        
    def manage_title_bar_visibility(self):
        pointer_y = self.root.winfo_pointery()
        win_y = self.root.winfo_y()
        if win_y <= pointer_y < win_y + self.TITLE_BAR_HOVER_HEIGHT:
            self.title_bar.place(x=0, y=0, relwidth=1)
        else:
            title_bar_y = self.title_bar.winfo_y()
            title_bar_height = self.title_bar.winfo_height()
            if pointer_y > title_bar_y + title_bar_height or pointer_y < title_bar_y:
                self.title_bar.place_forget()
        self.root.after(100, self.manage_title_bar_visibility)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            # 进入全屏时，隐藏拖拽角
            self.grip_br.place_forget()
            self.grip_bl.place_forget()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.fullscreen_button.config(text='◱')
        else:
            # 回到窗口模式时，显示拖拽角
            self.grip_br.place(relx=1.0, rely=1.0, anchor='se', width=15, height=15)
            self.grip_bl.place(relx=0.0, rely=1.0, anchor='sw', width=15, height=15)
            self.root.geometry(self.windowed_geometry)
            self.fullscreen_button.config(text='⛶')
        self.root.after(50, self.redraw_current_image)
    
    def on_close(self, event=None):
        self.root.destroy()
        
    def manual_next_image(self, event=None):
        if event and event.widget == self.image_label:
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.show_next_image()

    def create_custom_title_bar(self):
        self.title_bar = tk.Frame(self.root, bg='#282828')
        close_button = tk.Button(self.title_bar, text='✕', bg='#282828', fg='white', relief='flat', command=self.on_close, width=4)
        close_button.pack(side='right')
        self.fullscreen_button = tk.Button(self.title_bar, text='◱', bg='#282828', fg='white', relief='flat', command=self.toggle_fullscreen, width=4)
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
    """预扫描图片，计算最合适的初始窗口尺寸"""
    temp_root = tk.Tk()
    temp_root.withdraw()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()

    # 将最大尺寸限制调整为更紧凑的xx%
    max_win_width = screen_width * 0.25
    max_win_height = screen_height * 0.25
    
    target_w, target_h = 0, 0

    for filepath in tqdm(image_files, desc="正在分析图片库", unit="张"):
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
    
    if target_w < 200 or target_h < 200:
        return "640x480"

    return f"{int(target_w)}x{int(target_h)}"

def main():
    """程序主入口"""
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
    player = AdvancedImagePlayer(app_root, image_files, initial_geometry)
    app_root.mainloop()

if __name__ == "__main__":
    main()