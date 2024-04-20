import tkinter as tk
from PIL import Image, ImageTk
import os
import random

def list_images(directory):
    extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in extensions]

def update_image():
    global photo_image, update_id
    img_path = random.choice(images)
    img = Image.open(img_path)
    img = resize_image(img, root.winfo_width(), root.winfo_height())
    photo_image = ImageTk.PhotoImage(img)
    canvas.itemconfig(image_on_canvas, image=photo_image)
    # 重置定时器
    root.after_cancel(update_id)
    update_id = root.after(3000, update_image)

def resize_image(img, max_width, max_height):
    original_width, original_height = img.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

def on_key(event):
    if event.keysym == 'Escape':  # 检查是否是Esc键
        root.destroy()  # 按Esc键退出程序

def on_click(event):
    update_image()  # 鼠标点击立即更换图片

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(background='black')  # 设置背景为黑色

canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg='black', highlightthickness=0)
canvas.pack()

images = list_images('txt2img-images')
photo_image = None
image_on_canvas = canvas.create_image(root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2, anchor='center')

# 键盘和鼠标事件绑定
root.bind("<Key>", on_key)
root.bind("<Button-1>", on_click)  # 绑定鼠标左键
root.bind("<Button-3>", on_click)  # 绑定鼠标右键

# 初始化全局变量update_id并启动图片更新
update_id = root.after(100, update_image)

root.mainloop()
