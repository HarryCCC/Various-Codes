import tkinter as tk
from tkinter import messagebox
# 导入PIL模块，用于处理图片
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os, time, re, math

# 创建一个窗口对象
window = tk.Tk()
# 设置窗口标题
window.title("电子印章软件")
# 设置窗口大小
window.geometry("800x900")
# 获取屏幕的宽度和高度
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
# 计算窗口的左上角坐标
x = (screen_width) // 4
y = (screen_height) // 16
# 设置窗口的位置
window.geometry("+%d+%d" % (x, y))

# 创建一个画布对象，用于显示印章预览
canvas = tk.Canvas(window, width=400, height=400, bg="white")
# 将画布放在窗口的左侧
canvas.pack(side=tk.LEFT)

# 创建一个标签对象，用于显示参数调整的标题
label = tk.Label(window, text="参数调整", font=("Arial", 20))
# 将标签放在窗口的右上角
label.pack(side=tk.TOP)

text_var = tk.StringVar(value="国海证券有限责任公司")
# 创建一个输入框对象，用于输入印章的文字
entry = tk.Entry(window, font=("Arial", 15), textvariable=text_var)
# 将输入框放在窗口的右侧
entry.pack(side=tk.TOP, padx=10, pady=10)

# 创建一个滑动条对象，用于调整印章的文字直径
scale1 = tk.Scale(window, from_=0, to=300, orient=tk.HORIZONTAL, label="文字直径", font=("Arial", 15), resolution=1)
# 将滑动条放在窗口的右侧
scale1.pack(side=tk.TOP, padx=10, pady=10)

# 创建一个滑动条对象，用于调整印章的文字间隔
scale2 = tk.Scale(window, from_=80, to=100, orient=tk.HORIZONTAL, label="文字间隔", font=("Arial", 15), resolution=1)
# 将滑动条放在窗口的右侧
scale2.pack(side=tk.TOP, padx=10, pady=10)

# 创建一个滑动条对象，用于调整印章的文字角度
scale3 = tk.Scale(window, from_=47, to=360, orient=tk.HORIZONTAL, label="文字角度", font=("Arial", 15), resolution=1)
# 将滑动条放在窗口的右侧
scale3.pack(side=tk.TOP, padx=10, pady=10)

# 创建一个滑动条对象，用于调整印章的文字大小
scale4 = tk.Scale(window, from_=26, to=50, orient=tk.HORIZONTAL, label="文字大小", font=("Arial", 15), resolution=1)
# 将滑动条放在窗口的右侧
scale4.pack(side=tk.TOP, padx=10, pady=10)

# 创建一个选项框对象，用于选择印章的颜色
color_var = tk.StringVar()
color_var.set("#E50000")
option = tk.OptionMenu(window, color_var, "red", "blue", "green", "black", "#E50000")

option.config(font=("Arial", 15))
option.pack(side=tk.TOP, padx=10, pady=10)

# 在创建滑动条的下方，增加四个文本输入框，用于输入参数值，每个输入框的变量名为entry1, entry2, entry3, entry4
entry1_var = tk.StringVar()
entry1 = tk.Entry(window, font=("Arial", 15), textvariable=entry1_var)
entry1.pack(side=tk.TOP, padx=10, pady=10)
entry2_var = tk.StringVar()
entry2 = tk.Entry(window, font=("Arial", 15), textvariable=entry2_var)
entry2.pack(side=tk.TOP, padx=10, pady=10)
entry3_var = tk.StringVar()
entry3 = tk.Entry(window, font=("Arial", 15), textvariable=entry3_var)
entry3.pack(side=tk.TOP, padx=10, pady=10)
entry4_var = tk.StringVar()
entry4 = tk.Entry(window, font=("Arial", 15), textvariable=entry4_var)
entry4.pack(side=tk.TOP, padx=10, pady=10)

# 定义一个函数，用于生成印章图片
def generate_stamp():
    # 获取输入框的内容
    text = entry.get()
    # 获取滑动条的值
    diameter = scale1.get()
    spacing = scale2.get()
    angle = scale3.get()
    size = scale4.get()
    # 获取选项框的值
    color = color_var.get()
    # 获取文本输入框的内容
    entry1_text = entry1_var.get()
    entry2_text = entry2_var.get()
    entry3_text = entry3_var.get()
    entry4_text = entry4_var.get()
    # 判断文本输入框的内容是否为数字，如果是，就用输入框中的值作为参数，否则用滑动条的值作为参数
    if re.match(r"^\d+$", entry1_text):
        diameter = int(entry1_text)
    if re.match(r"^\d+$", entry2_text):
        spacing = int(entry2_text)
    if re.match(r"^\d+$", entry3_text):
        angle = int(entry3_text)
    if re.match(r"^\d+$", entry4_text):
        size = int(entry4_text)
    # 创建一个透明背景的图片对象，大小为400x400
    image = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    # 创建一个绘图对象，用于在图片上绘制文字和外框
    draw = ImageDraw.Draw(image)
    # 创建一个字体对象，用于设置文字的字体和大小
    font = ImageFont.truetype("C:\Windows\Fonts\simkai.ttf", size)
    # 计算文字的长度
    length = len(text)
    # 计算每个文字的角度增量
    delta = (360 - 120) / length
    # 计算文字的总弧长
    arc_length = diameter * math.pi * delta / 180
    # 计算文字的最大间隔
    max_spacing = arc_length - font.getbbox(text[0])[0]

    # 绘制一个圆形的印章外框，颜色为印章颜色
    draw.ellipse((100, 100, 300, 300), outline=color, width=5)

    # 在印章的中心绘制一个五角星
    # 计算五角星的五个顶点
    star_points = [(200 + 50 * math.cos(i * 2 * math.pi / 5), 200 + 50 * math.sin(i * 2 * math.pi / 5)) for i in range(5)]
    # 重新排列五角星的顶点，使得它是正五角星
    star_points = [star_points[i] for i in [0, 2, 4, 1, 3]]
    # 绘制五角星，颜色为印章颜色，填充颜色也为印章颜色
    draw.polygon(star_points, fill=color, outline=color)

    # 在印章的中心绘制一个实心的圆形，颜色为印章颜色
    draw.ellipse((180, 180, 220, 220), fill=color, outline=color)

    # 在五角星的下方添加一行文字，颜色和大小与环绕文字一致
    bottom_text = "人力资源部"
    # 计算文字的角度
    theta = (angle + 135) % 360
    # 将角度转换为弧度
    rad = theta * 3.14159 / 180
    # 计算当前文字的坐标
    x = 262 + (diameter / 2 + spacing) * math.cos(rad)
    y = 256 + (diameter / 2 + spacing) * math.sin(rad)
    # 创建一个新的图片对象，用于旋转文字
    text_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)
    # 将当前文字绘制在新的图片上，颜色为印章颜色
    text_draw.text((x, y), bottom_text, fill=color, font=font, anchor="mm")
    # 旋转文字图片
    rotated_text_img = text_img.rotate(-theta + 162, center=(x, y))
    # 将旋转后的文字图片合并到印章图片上
    image = Image.alpha_composite(image, rotated_text_img)

    # 遍历每个文字
    for i in range(length):
        # 计算当前文字的角度
        theta = (angle + 135 + i * delta) % 360
        # 将角度转换为弧度
        rad = theta * 3.14159 / 180
        # 计算当前文字的坐标
        x = 200 + (diameter / 2 + spacing) * math.cos(rad)
        y = 200 + (diameter / 2 + spacing) * math.sin(rad)
        # 创建一个新的图片对象，用于旋转文字
        text_img = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        # 将当前文字绘制在新的图片上，颜色为印章颜色
        text_draw.text((x, y), text[i], fill=color, font=font, anchor="mm")
        # 旋转文字图片
        rotated_text_img = text_img.rotate(-theta - 90, center=(x, y))
        # 将旋转后的文字图片合并到印章图片上
        image = Image.alpha_composite(image, rotated_text_img)
    

    # 返回图片对象
    return image

# 定义一个函数，用于更新印章预览
def update_canvas():
    text = text_var.get()
    # 调用生成印章图片的函数
    image = generate_stamp()
    # 将图片对象转换为tkinter可用的图片对象
    photo = ImageTk.PhotoImage(image)
    # 在画布上显示图片
    canvas.create_image(200, 200, image=photo)
    # 将图片对象保存为全局变量，防止被垃圾回收
    global stamp_photo
    stamp_photo = photo

# 创建一个按钮对象，用于更新印章预览
button = tk.Button(window, text="更新印章预览", font=("Arial", 15), command=update_canvas)
# 将按钮放在窗口的右下角
button.pack(side=tk.BOTTOM, padx=10, pady=10)

# 创建一个函数，用于保存印章图片
def save_stamp():
    # 调用生成印章图片的函数
    image = generate_stamp()
    # 获取当前目录路径
    path = os.getcwd()
    # 拼接图片文件名，使用时间戳作为唯一标识
    filename = "stamp_" + str(int(time.time())) + ".png"
    # 保存图片到当前目录
    image.save(os.path.join(path, filename))
    # 弹出提示框，显示保存成功的信息
    tk.messagebox.showinfo("提示", "印章图片已保存到" + filename)

# 创建一个按钮对象，用于保存印章图片
save_button = tk.Button(window, text="保存印章图片", font=("Arial", 15), command=save_stamp)
# 将按钮放在窗口的右下角
save_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# 进入窗口的主循环
window.mainloop()

