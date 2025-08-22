# -*- coding: utf-8 -*-

"""
高级图片播放器
版本 5.3.0 (角标拖拽版):
- 移除了图片边缘拖拽功能，以解决交互不稳定的问题。
- 在窗口的左下角和右下角添加了两个可见的、专门用于调整尺寸的拖拽角标。
- 角标在全屏模式下会自动隐藏。
- 单击图片中心区域依旧是切换下一张图片。
- 初始窗口位置调整到屏幕左下角，位于任务栏之上。
"""

import tkinter as tk
from tkinter import messagebox
import os
import random
from PIL import Image, ImageTk, ImageOps, ImageFilter
import sys

# --- 全局参数 ---
TIME_INTERVAL_SECONDS = 3
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
        self._resize_data = {"x": 0, "y": 0, "w": 0, "h": 0, "x_win": 0, "y_win": 0, "mode": ""}

        self.root.title("图片播放器")
        self.root.configure(bg='black')
        
        self.root.overrideredirect(True)
        self.root.geometry(self.windowed_geometry)
        self.root.attributes('-topmost', self.is_pinned)

        self.background_label = tk.Label(self.root, bg='black')
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.image_label = tk.Label(self.root, bg='black')
        self.image_label.place(in_=self.background_label, anchor="center", relx=0.5, rely=0.5)
        
        self.create_custom_title_bar()
        self.setup_resize_grips() # 创建拖拽角标
        self.pin_button.config(fg='cyan')

        # --- 事件绑定 ---
        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<Configure>", self.on_configure)
        self.root.bind("<space>", self.toggle_fullscreen)
        self.root.bind("<Button-3>", self.toggle_fullscreen)
        
        self.image_label.bind("<Button-1>", self.manual_next_image) # 图片单击切换
        self.image_label.bind("<Button-3>", self.toggle_fullscreen)

        self.root.after(50, self.start_application)

    def start_application(self):
        """在窗口稳定后，启动所有动态功能"""
        self.show_next_image()
        self.manage_title_bar_visibility_on_hover()

    def on_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            self.on_close()

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
        
    def manage_title_bar_visibility_on_hover(self):
        if self.is_fullscreen:
            pointer_y = self.root.winfo_pointery()
            if 0 <= pointer_y <= self.TITLE_BAR_HOVER_HEIGHT:
                self.title_bar.place(x=0, y=0, relwidth=1, height=30)
            else:
                title_bar_y = self.title_bar.winfo_y()
                title_bar_height = self.title_bar.winfo_height()
                if pointer_y > title_bar_y + title_bar_height or pointer_y < title_bar_y:
                    self.title_bar.place_forget()
        self.root.after(100, self.manage_title_bar_visibility_on_hover)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            self.windowed_geometry = self.root.geometry()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self.fullscreen_button.config(text='◱')
            self.grip_corner_se.place_forget()
            self.grip_corner_sw.place_forget()
        else:
            self.root.geometry(self.windowed_geometry)
            self.fullscreen_button.config(text='⛶')
            self.title_bar.place(x=0, y=0, relwidth=1, height=30)
            self.grip_corner_se.place(relx=1.0, rely=1.0, anchor='se')
            self.grip_corner_sw.place(relx=0.0, rely=1.0, anchor='sw')
        
        self.root.after(50, self.update_image_display)
    
    def on_close(self, event=None):
        self.root.destroy()
        
    def manual_next_image(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.show_next_image()

    def create_custom_title_bar(self):
        self.title_bar = tk.Frame(self.root, bg='#282828', height=30)
        self.title_bar.place(x=0, y=0, relwidth=1, height=30)

        close_button = tk.Button(self.title_bar, text='✕', bg='#282828', fg='white', relief='flat', command=self.on_close, width=4)
        close_button.pack(side='right')
        self.fullscreen_button = tk.Button(self.title_bar, text='⛶', bg='#282828', fg='white', relief='flat', command=self.toggle_fullscreen, width=4)
        self.fullscreen_button.pack(side='right')
        self.pin_button = tk.Button(self.title_bar, text='📌', bg='#282828', fg='white', relief='flat', command=self.toggle_pin, width=4)
        self.pin_button.pack(side='right')
        
        drag_handle = tk.Label(self.title_bar, bg='#282828', text="  图片播放器", fg="white")
        drag_handle.pack(side='left', fill='x', expand=True)
        
        for widget in [self.title_bar, drag_handle, close_button, self.fullscreen_button, self.pin_button]:
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)

    def setup_resize_grips(self):
        """创建用于调整窗口大小的角标"""
        self.grip_corner_se = tk.Label(self.root, text='◢', bg='black', fg='#555', cursor='sizing', font=("Courier", 10))
        self.grip_corner_se.place(relx=1.0, rely=1.0, anchor='se')
        self.grip_corner_se.bind("<ButtonPress-1>", lambda e: self._on_resize_press(e, "se"))
        self.grip_corner_se.bind("<B1-Motion>", self._on_resize_motion)

        self.grip_corner_sw = tk.Label(self.root, text='◣', bg='black', fg='#555', cursor='sizing', font=("Courier", 10))
        self.grip_corner_sw.place(relx=0.0, rely=1.0, anchor='sw')
        self.grip_corner_sw.bind("<ButtonPress-1>", lambda e: self._on_resize_press(e, "sw"))
        self.grip_corner_sw.bind("<B1-Motion>", self._on_resize_motion)

    def toggle_pin(self, event=None):
        self.is_pinned = not self.is_pinned
        self.root.attributes('-topmost', self.is_pinned)
        self.pin_button.config(fg='cyan' if self.is_pinned else 'white')
        
    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root

    def _on_drag_motion(self, event):
        if not self.is_fullscreen:
            dx = event.x_root - self._drag_data["x"]
            dy = event.y_root - self._drag_data["y"]
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")
            self._drag_data["x"] = event.x_root
            self._drag_data["y"] = event.y_root
            
    def _on_resize_press(self, event, mode):
        """记录开始调整大小时的初始信息"""
        self.root.update_idletasks()
        self._resize_data['x'] = event.x_root
        self._resize_data['y'] = event.y_root
        self._resize_data['w'] = self.root.winfo_width()
        self._resize_data['h'] = self.root.winfo_height()
        self._resize_data['x_win'] = self.root.winfo_x()
        self._resize_data['y_win'] = self.root.winfo_y()
        self._resize_data['mode'] = mode

    def _on_resize_motion(self, event):
        """根据鼠标移动计算并应用新的窗口尺寸"""
        if not self._resize_data['mode']:
            return

        dx = event.x_root - self._resize_data['x']
        dy = event.y_root - self._resize_data['y']
        
        mode = self._resize_data['mode']

        if mode == "se":
            new_width = self._resize_data['w'] + dx
            new_height = self._resize_data['h'] + dy
            if new_width < 100: new_width = 100
            if new_height < 100: new_height = 100
            self.root.geometry(f"{new_width}x{new_height}")
        
        elif mode == "sw":
            new_width = self._resize_data['w'] - dx
            new_height = self._resize_data['h'] + dy
            if new_width < 100: new_width = 100
            if new_height < 100: new_height = 100
            
            new_x = self._resize_data['x_win'] + dx
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{self._resize_data['y_win']}")

def calculate_initial_geometry(image_files: list) -> str:
    """
    预扫描图片，基于所有图片的平均尺寸计算最合适的初始窗口尺寸和位置。
    """
    try:
        temp_root = tk.Tk()
        temp_root.withdraw()
        screen_width = temp_root.winfo_screenwidth()
        screen_height = temp_root.winfo_screenheight()
        temp_root.destroy()
    except tk.TclError:
        return "600x450+50+50"

    max_win_width = screen_width * 0.35
    max_win_height = screen_height * 0.35
    
    total_width = 0
    total_height = 0
    image_count = 0

    for filepath in image_files:
        try:
            with Image.open(filepath) as img:
                img_w, img_h = img.size
                total_width += img_w
                total_height += img_h
                image_count += 1
        except Exception:
            continue
    
    if image_count == 0:
        return "600x450+50+50"

    avg_w = total_width / image_count
    avg_h = total_height / image_count

    scale = 1.0
    if avg_w > max_win_width or avg_h > max_win_height:
        scale = min(max_win_width / avg_w, max_win_height / avg_h)

    target_w = int(avg_w * scale)
    target_h = int(avg_h * scale)

    if target_w < 200 or target_h < 200:
        target_w, target_h = 400, 300

    x_pos = 50
    taskbar_height_estimate = 80
    y_pos = screen_height - target_h - taskbar_height_estimate
    
    if y_pos < 50:
        y_pos = 50

    return f"{target_w}x{target_h}+{x_pos}+{y_pos}"

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
    player = AdvancedImagePlayer(app_root, image_files, initial_geometry)
    app_root.mainloop()

if __name__ == "__main__":
    main()
