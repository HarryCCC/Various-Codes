# -*- coding: utf-8 -*-

"""
高级图片播放器 (双屏同步版)
版本 6.5.0 (任务栏启动图标修复版):
- [修复] 解决了程序启动时任务栏不显示图标的问题。
- [方案] 不再使用 withdraw() 方法隐藏主窗口，而是将其移动到屏幕外。这能确保操作系统从一开始就为其注册一个任务栏图标。
- [重构] 采用主从窗口架构，从根本上解决了无边框窗口无法在任务栏常驻图标的问题。
           - 创建一个隐藏的Tk()主窗口作为任务栏图标的“所有者”。
           - 将播放器界面放在一个无边框的Toplevel()窗口中。
- [修复] 最小化功能现在能正确地将应用图标显示在任务栏，并能从任务栏恢复。
- 左侧目录: D:/GAMES/ComfyUI-aki/ComfyUI-aki-v1.6/ComfyUI/output/GreatAsFuck
- 右侧目录: C:/Users/Administrator/Desktop/ALBUM/PORTRAIT/Miyeon
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
# --- 修改为指定的绝对路径 ---
LEFT_IMAGE_DIR = r"D:\GAMES\ComfyUI-aki\ComfyUI-aki-v1.6\ComfyUI\output\GreatAsFuck"
RIGHT_IMAGE_DIR = r"C:\Users\Administrator\Desktop\ALBUM\PORTRAIT\Miyeon"


# --- HEIF/HEIC格式支持 ---
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

# --- 主程序类 ---
class AdvancedImagePlayer:
    TITLE_BAR_HOVER_HEIGHT = 40

    def __init__(self, root, master, image_files_left, image_files_right, initial_geometry):
        self.root = root  # 这是 Toplevel 播放器窗口
        self.master = master  # 这是隐藏的 Tk() 主窗口，用于控制任务栏图标
        self.image_files_left = image_files_left
        self.image_files_right = image_files_right
        self.current_index = -1
        self.after_id = None
        self.resize_job = None
        self.is_updating = False

        self.is_fullscreen = False
        self.is_pinned = True
        self.windowed_geometry = initial_geometry
        self._drag_data = {"x": 0, "y": 0}
        self._resize_data = {"x": 0, "y": 0, "w": 0, "h": 0, "x_win": 0, "y_win": 0, "mode": ""}

        # --- 强引用持有者：用于防止图片被垃圾回收 ---
        self.photo_references = {
            'left_bg': None, 'left_fg': None,
            'right_bg': None, 'right_fg': None
        }

        self.master.title("图片播放器 (双屏版)") # 为任务栏设置标题
        self.root.title("图片播放器 (双屏版)")
        self.root.configure(bg='black')
        
        self.root.overrideredirect(True)
        self.root.geometry(self.windowed_geometry)
        self.root.attributes('-topmost', self.is_pinned)

        # --- 创建左右两个独立的显示框架 ---
        self.left_frame = tk.Frame(self.root, bg='black')
        self.left_frame.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        self.right_frame = tk.Frame(self.root, bg='black')
        self.right_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        # --- 左侧UI元素 ---
        self.background_label_left = tk.Label(self.left_frame, bg='black')
        self.background_label_left.place(x=0, y=0, relwidth=1, relheight=1)
        self.image_label_left = tk.Label(self.left_frame, bg='black')
        self.image_label_left.place(in_=self.background_label_left, anchor="center", relx=0.5, rely=0.5)

        # --- 右侧UI元素 ---
        self.background_label_right = tk.Label(self.right_frame, bg='black')
        self.background_label_right.place(x=0, y=0, relwidth=1, relheight=1)
        self.image_label_right = tk.Label(self.right_frame, bg='black')
        self.image_label_right.place(in_=self.background_label_right, anchor="center", relx=0.5, rely=0.5)
        
        self.create_custom_title_bar()
        self.setup_resize_grips()
        self.pin_button.config(fg='cyan')

        # --- 事件绑定 ---
        self.master.bind("<Map>", self.on_restore_from_minimize) # 绑定到主窗口的恢复事件
        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<Configure>", self.on_configure)
        self.root.bind("<space>", self.toggle_fullscreen)
        self.root.bind("<Button-3>", self.toggle_fullscreen)
        
        for widget in [self.image_label_left, self.image_label_right, self.left_frame, self.right_frame]:
            widget.bind("<Button-1>", self.manual_next_image)
            widget.bind("<Button-3>", self.toggle_fullscreen)

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
        if not self.is_fullscreen and self.root.winfo_viewable():
            self.windowed_geometry = self.root.geometry()
        if self.resize_job:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(150, self.update_image_display)
    
    # --- 架构重构核心部分 ---

    def _prepare_panel_photos(self, side):
        """
        准备阶段：创建并返回一个面板所需的所有PhotoImage对象。
        此函数不修改任何实例变量，确保操作的纯粹性和安全性。
        """
        if side == 'left':
            frame, image_label = self.left_frame, self.image_label_left
        else: # right
            frame, image_label = self.right_frame, self.image_label_right
        
        if not hasattr(image_label, 'current_pil_image') or image_label.current_pil_image is None:
            return None, None

        bg_photo, fg_photo = None, None
        original_img = image_label.current_pil_image.convert("RGB")
        win_width = frame.winfo_width()
        win_height = frame.winfo_height()
        if win_width <= 1 or win_height <= 1:
            return None, None

        # --- 背景处理 ---
        try:
            bg_img = original_img.resize((win_width // 10, win_height // 10), Image.Resampling.BOX)
            bg_img = bg_img.filter(ImageFilter.GaussianBlur(BLUR_RADIUS))
            bg_img = bg_img.resize((win_width, win_height), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_img)
        except Exception as e:
            print(f"创建背景PhotoImage时出错 ({side}): {e}")
            bg_photo = None
        
        # --- 前景处理 ---
        try:
            img_width, img_height = original_img.size
            scale = min(win_width / img_width, win_height / img_height)
            new_width, new_height = int(img_width * scale), int(img_height * scale)
            
            if new_width > 0 and new_height > 0:
                resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                fg_photo = ImageTk.PhotoImage(resized_img)
        except Exception as e:
            print(f"创建前景PhotoImage时出错 ({side}): {e}")
            fg_photo = None
            
        return bg_photo, fg_photo

    def update_image_display(self):
        """
        统一的显示更新调度函数。
        核心修复：先将新图片配置给组件，再更新引用持有者，杜绝时序竞争。
        """
        if self.is_updating or not self.root.winfo_exists():
            return
        
        self.is_updating = True
        try:
            # 1. 准备阶段：安全地创建所有新图像
            left_bg_photo, left_fg_photo = self._prepare_panel_photos('left')
            right_bg_photo, right_fg_photo = self._prepare_panel_photos('right')
            
            # 2. 应用与引用更新阶段 (关键修复)
            #    先将新图像赋给Label，让Tkinter持有其内部引用
            #    然后再更新我们自己的Python引用持有者
            
            # 左侧面板
            self.background_label_left.config(image=left_bg_photo or '')
            self.photo_references['left_bg'] = left_bg_photo
            
            self.image_label_left.config(image=left_fg_photo or '')
            self.photo_references['left_fg'] = left_fg_photo
            if left_fg_photo:
                self.image_label_left.config(width=left_fg_photo.width(), height=left_fg_photo.height())

            # 右侧面板
            self.background_label_right.config(image=right_bg_photo or '')
            self.photo_references['right_bg'] = right_bg_photo
            
            self.image_label_right.config(image=right_fg_photo or '')
            self.photo_references['right_fg'] = right_fg_photo
            if right_fg_photo:
                self.image_label_right.config(width=right_fg_photo.width(), height=right_fg_photo.height())

        except Exception as e:
            # 这个最终的try/except是为了捕获所有意外，例如Tkinter窗口销毁时可能发生的错误
            if "invalid command name" not in str(e):
                print(f"更新显示时发生意外的顶层错误: {e}")
        finally:
            self.is_updating = False # 释放锁
            
    # --- 结束重构 ---

    def show_next_image(self):
        """加载下一组PIL图片到内存，并触发显示更新。"""
        if not self.root.winfo_exists():
            return
            
        if self.root.winfo_width() <= 1 or self.root.winfo_height() <= 1:
            self.after_id = self.root.after(100, self.show_next_image)
            return

        self.current_index += 1
        
        # 加载左侧PIL图片
        if self.image_files_left:
            image_path = self.image_files_left[self.current_index % len(self.image_files_left)]
            try:
                with Image.open(image_path) as img:
                    # 移除可能导致问题的ICC配置文件
                    if 'icc_profile' in img.info: del img.info['icc_profile']
                    self.image_label_left.current_pil_image = ImageOps.exif_transpose(img)
            except Exception as e:
                print(f"无法加载左侧图片 '{os.path.basename(image_path)}': {e}")
                self.image_label_left.current_pil_image = None
        else:
            self.image_label_left.current_pil_image = None

        # 加载右侧PIL图片
        if self.image_files_right:
            image_path = self.image_files_right[self.current_index % len(self.image_files_right)]
            try:
                with Image.open(image_path) as img:
                    if 'icc_profile' in img.info: del img.info['icc_profile']
                    self.image_label_right.current_pil_image = ImageOps.exif_transpose(img)
            except Exception as e:
                print(f"无法加载右侧图片 '{os.path.basename(image_path)}': {e}")
                self.image_label_right.current_pil_image = None
        else:
            self.image_label_right.current_pil_image = None
            
        if self.root.winfo_exists():
            self.update_image_display()
            # 取消旧的计时器（如果有），以防手动切换和自动播放冲突
            if self.after_id:
                self.root.after_cancel(self.after_id)
            self.after_id = self.root.after(TIME_INTERVAL_SECONDS * 1000, self.show_next_image)

    def manage_title_bar_visibility_on_hover(self):
        try:
            if self.root.winfo_exists() and self.is_fullscreen:
                pointer_y = self.root.winfo_pointery()
                if 0 <= pointer_y <= self.TITLE_BAR_HOVER_HEIGHT:
                    self.title_bar.place(x=0, y=0, relwidth=1, height=30)
                else:
                    title_bar_y = self.title_bar.winfo_y()
                    if pointer_y > title_bar_y + 30 or pointer_y < title_bar_y:
                        self.title_bar.place_forget()
        except tk.TclError: # 窗口销毁时可能报错
            pass
        
        if self.root.winfo_exists():
            self.root.after(100, self.manage_title_bar_visibility_on_hover)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            # 进入全屏前，如果窗口可见，则保存当前几何信息
            if self.root.winfo_viewable():
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
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.master.destroy() # 销毁主窗口，Toplevel子窗口也会被一并销毁

    def minimize_window(self, event=None):
        """最小化窗口到任务栏"""
        self.root.withdraw()
        self.master.iconify()
        
    def on_restore_from_minimize(self, event=None):
        """当窗口从最小化状态恢复时调用"""
        self.root.deiconify()
        self.root.attributes('-topmost', self.is_pinned)

    def manual_next_image(self, event=None):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.show_next_image()

    def create_custom_title_bar(self):
        self.title_bar = tk.Frame(self.root, bg='#282828', height=30)
        self.title_bar.place(x=0, y=0, relwidth=1, height=30)

        # 按钮从右向左依次排列
        close_button = tk.Button(self.title_bar, text='✕', bg='#282828', fg='white', relief='flat', command=self.on_close, width=4)
        close_button.pack(side='right')

        self.fullscreen_button = tk.Button(self.title_bar, text='⛶', bg='#282828', fg='white', relief='flat', command=self.toggle_fullscreen, width=4)
        self.fullscreen_button.pack(side='right')
        
        # 新增的最小化按钮
        minimize_button = tk.Button(self.title_bar, text='—', bg='#282828', fg='white', relief='flat', command=self.minimize_window, width=4)
        minimize_button.pack(side='right')

        self.pin_button = tk.Button(self.title_bar, text='📌', bg='#282828', fg='white', relief='flat', command=self.toggle_pin, width=4)
        self.pin_button.pack(side='right')
        
        drag_handle = tk.Label(self.title_bar, bg='#282828', text="   图片播放器 (双屏版)", fg="white")
        drag_handle.pack(side='left', fill='x', expand=True)
        
        for widget in [self.title_bar, drag_handle]:
            widget.bind("<ButtonPress-1>", self._on_drag_start)
            widget.bind("<B1-Motion>", self._on_drag_motion)

    def setup_resize_grips(self):
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
        if self.is_fullscreen: return
        dx = event.x_root - self._drag_data["x"]
        dy = event.y_root - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root
            
    def _on_resize_press(self, event, mode):
        self.root.update_idletasks()
        self._resize_data.update({
            'x': event.x_root, 'y': event.y_root,
            'w': self.root.winfo_width(), 'h': self.root.winfo_height(),
            'x_win': self.root.winfo_x(), 'y_win': self.root.winfo_y(),
            'mode': mode
        })

    def _on_resize_motion(self, event):
        if not self._resize_data['mode']: return

        dx = event.x_root - self._resize_data['x']
        dy = event.y_root - self._resize_data['y']
        
        if self._resize_data['mode'] == "se":
            new_width = max(200, self._resize_data['w'] + dx)
            new_height = max(100, self._resize_data['h'] + dy)
            self.root.geometry(f"{new_width}x{new_height}")
        
        elif self._resize_data['mode'] == "sw":
            new_width = max(200, self._resize_data['w'] - dx)
            new_height = max(100, self._resize_data['h'] + dy)
            new_x = self._resize_data['x_win'] + dx
            self.root.geometry(f"{new_width}x{new_height}+{new_x}+{self._resize_data['y_win']}")

def calculate_initial_geometry(root, all_image_files: list) -> str:
    try:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
    except tk.TclError:
        return "800x450+50+50"

    max_win_width = screen_width * 0.7
    max_win_height = screen_height * 0.7
    total_width, total_height, image_count = 0, 0, 0

    for filepath in all_image_files[:50]: # Scan up to 50 images for performance
        try:
            with Image.open(filepath) as img:
                img_w, img_h = img.size
                total_width += img_w
                total_height += img_h
                image_count += 1
        except Exception: continue
    
    if image_count == 0: return "800x450+50+50"

    avg_w = total_width / image_count
    avg_h = total_height / image_count
    scale = 1.0
    if avg_w * 2 > max_win_width or avg_h > max_win_height:
        scale = min(max_win_width / (avg_w * 2), max_win_height / avg_h)

    target_w = int(avg_w * scale * 2)
    target_h = int(avg_h * scale)
    target_w, target_h = max(400, target_w), max(200, target_h)

    x_pos = 5
    y_pos = screen_height - target_h - 50 # 50 for taskbar
    return f"{target_w}x{target_h}+{x_pos}+{max(5, y_pos)}"

def main():
    master_root = tk.Tk()
    # 将主窗口移出屏幕以隐藏它，同时保留其在任务栏上的图标。
    # 这是比 withdraw() 更可靠的方法，能确保任务栏图标从一开始就存在。
    master_root.geometry("+9999+9999")

    for path in [LEFT_IMAGE_DIR, RIGHT_IMAGE_DIR]:
        if not os.path.isdir(path):
            messagebox.showerror("目录错误", f"图片目录不存在或无效:\n{path}")
            master_root.destroy()
            return

    image_files_left = sorted([os.path.join(LEFT_IMAGE_DIR, f) for f in os.listdir(LEFT_IMAGE_DIR) if f.lower().endswith(SUPPORTED_EXTENSIONS)])
    image_files_right = sorted([os.path.join(RIGHT_IMAGE_DIR, f) for f in os.listdir(RIGHT_IMAGE_DIR) if f.lower().endswith(SUPPORTED_EXTENSIONS)])
    random.shuffle(image_files_left)
    random.shuffle(image_files_right)

    if not image_files_left and not image_files_right:
        messagebox.showwarning("未找到图片", "在指定的两个目录中均未找到任何支持的图片文件。")
        master_root.destroy()
        return

    # 创建实际的播放器窗口，作为隐藏主窗口的子窗口
    player_window = tk.Toplevel(master_root)

    initial_geometry = calculate_initial_geometry(master_root, image_files_left + image_files_right)
    
    player = AdvancedImagePlayer(player_window, master_root, image_files_left, image_files_right, initial_geometry)
    
    master_root.mainloop()

if __name__ == "__main__":
    main()

