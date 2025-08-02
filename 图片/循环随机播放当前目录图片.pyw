# -*- coding: utf-8 -*-

"""
一个全屏、随机、可交互的图片轮播浏览器
版本: 1.1
功能:
- 随机循环播放当前目录下的所有主流格式图片
- 支持格式: webp, jpg, jpeg, png, gif, bmp, heic, heif
- 鼠标左键: 立即切换到下一张随机图片
- 鼠标右键 或 ESC键: 退出程序
- 可在下方参数区域调整图片自动切换的时间间隔
"""

import tkinter as tk
from tkinter import messagebox
import os
import random
from PIL import Image, ImageTk, ImageOps
import sys

# 尝试导入HEIF支持库，如果失败则在后续进行提示
try:
    import pillow_heif
    # 注册HEIF/HEIC格式的解码器
    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:
    HEIF_SUPPORTED = False

# --- 可调参数 ---
# 图片自动切换的时间间隔（单位：秒）
TIME_INTERVAL_SECONDS = 2

# 支持的图片文件扩展名 (小写)
SUPPORTED_EXTENSIONS = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')

class FullScreenImagePlayer:
    """
    全屏图片播放器主类
    """
    def __init__(self, root, image_files):
        self.root = root
        self.image_files = image_files
        self.current_index = -1
        self.after_id = None

        # --- UI 初始化 ---
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind("<Escape>", self.exit_player)
        self.root.bind("<Button-3>", self.exit_player) # 鼠标右键
        self.root.bind("<Button-1>", self.manual_next_image) # 鼠标左键

        self.image_label = tk.Label(self.root, bg='black')
        self.image_label.pack(expand=True, fill='both')
        
        # 启动播放
        self.show_next_image()

    def show_next_image(self):
        """核心功能：加载、处理并显示下一张图片"""
        # 循环播放
        self.current_index = (self.current_index + 1) % len(self.image_files)
        image_path = self.image_files[self.current_index]

        try:
            # --- 图片加载与处理 ---
            # 1. 打开图片
            with Image.open(image_path) as img:
                # 2. 修正图片方向 (尤其重要，用于修复手机照片的旋转问题)
                img = ImageOps.exif_transpose(img)

                # 3. 计算缩放尺寸以适应屏幕，同时保持宽高比
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                img_width, img_height = img.size

                scale_w = screen_width / img_width
                scale_h = screen_height / img_height
                scale = min(scale_w, scale_h)

                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # 4. 高质量缩放图片
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 5. 转换为Tkinter兼容格式并显示
                photo_image = ImageTk.PhotoImage(resized_img)
                self.image_label.config(image=photo_image)
                # !! 关键: 必须保留对photo_image的引用，否则会被Python垃圾回收，导致图片不显示
                self.image_label.image = photo_image

        except Exception as e:
            print(f"错误：无法加载或处理图片 '{os.path.basename(image_path)}'.\n原因: {e}")
            # 跳过损坏的图片，直接尝试下一张
            self.root.after(100, self.show_next_image) # 稍作延迟后继续
            return

        # 安排下一次自动切换
        self.after_id = self.root.after(TIME_INTERVAL_SECONDS * 1000, self.show_next_image)

    def manual_next_image(self, event=None):
        """手动切换图片"""
        # 取消之前安排的自动切换任务
        if self.after_id:
            self.root.after_cancel(self.after_id)
        # 立即显示下一张
        self.show_next_image()

    def exit_player(self, event=None):
        """退出程序"""
        self.root.destroy()


def main():
    """主函数：查找图片并启动播放器"""
    try:
        # 在打包成单个exe文件时，sys._MEIPASS是PyInstaller创建的临时文件夹路径
        if hasattr(sys, '_MEIPASS'):
            current_directory = os.path.dirname(sys.executable)
        else:
            # 正常运行时，获取脚本所在目录
            current_directory = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 在某些IDE的交互式环境中__file__可能未定义
        current_directory = os.getcwd()

    all_files = os.listdir(current_directory)
    image_files = [
        os.path.join(current_directory, f) for f in all_files 
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    
    # 随机打乱图片顺序
    random.shuffle(image_files)

    if not image_files:
        root = tk.Tk()
        root.withdraw() # 隐藏主窗口
        messagebox.showwarning("未找到图片", f"在当前目录下未找到任何支持的图片文件。\n支持的格式: {', '.join(SUPPORTED_EXTENSIONS)}")
        if not HEIF_SUPPORTED and any(f.lower().endswith(('.heic', '.heif')) for f in all_files):
            messagebox.showinfo("HEIF/HEIC 提示", "检测到HEIC/HEIF格式图片，但缺少 'pillow-heif' 库支持。\n请通过 'pip install pillow-heif' 命令安装。")
        root.destroy()
        return

    # 初始化并运行Tkinter应用
    app_root = tk.Tk()
    player = FullScreenImagePlayer(app_root, image_files)
    app_root.mainloop()

if __name__ == "__main__":
    main()