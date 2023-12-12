import cv2
import os

def blur_current_directory_image(blur_level=5):
    """
    在当前脚本所在的目录中查找图片并进行虚化处理。
    
    参数:
        blur_level (int): 虚化的程度。数值越大，虚化效果越明显。
        
    返回:
        None
    """
    # 获取当前脚本所在的路径
    current_path = os.path.dirname(os.path.abspath(__file__))

    # 定义支持的图片格式
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']

    # 在当前路径中查找支持的图片文件
    image_files = [f for f in os.listdir(current_path) if os.path.splitext(f)[1].lower() in supported_formats]
    
    if not image_files:
        print("未在当前目录找到支持的图片文件。")
        return
    
    if len(image_files) > 1:
        print("在当前目录找到多个图片文件，请只保留一个输入图片。")
        return

    input_filename = image_files[0]
    input_path = os.path.join(current_path, input_filename)
    
    # 生成输出文件名
    base_name, ext = os.path.splitext(input_filename)
    output_filename = f"{base_name}_blur{ext}"
    output_path = os.path.join(current_path, output_filename)

    # 读取图像
    img = cv2.imread(input_path)
    
    # 使用高斯模糊进行虚化
    blurred = cv2.GaussianBlur(img, (blur_level*2+1, blur_level*2+1), 0)
    
    # 保存虚化后的图像
    cv2.imwrite(output_path, blurred)
    print(f"已生成虚化图片: {output_filename}")

# 使用示例
blur_current_directory_image(blur_level=100)
