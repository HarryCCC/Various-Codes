from PIL import Image
import os

def png_to_ico(png_path, ico_path):
    # 打开PNG图片
    img = Image.open(png_path)
    
    # 将图片转换为RGBA格式（如果需要）
    img = img.convert('RGBA')
    
    # 保存为ICO文件
    img.save(ico_path, format='ICO')

# 假设PNG和ICO文件位于当前目录下
current_path = 'C:/Users/11470/Desktop/新建文件夹'  # 这里仅作为演示，在实际使用中，您可能会使用不同的路径
png_path = os.path.join(current_path, '123.png')
ico_path = os.path.join(current_path, '123.ico')

# 执行转换
png_to_ico(png_path, ico_path)

ico_path