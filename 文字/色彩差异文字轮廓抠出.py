import os
import cv2
import numpy as np

def extract_text(image_path, min_area_threshold=10):
    # 读取图片
    image = cv2.imread(image_path)
    
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 对图像进行高斯滤波，降低噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 使用 Canny 算法进行边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    
    # 对边缘图像进行膨胀操作，连接断开的边缘
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 使用边缘图像作为掩码，从原图中抠出文字
    mask = cv2.cvtColor(dilated_edges, cv2.COLOR_GRAY2BGR)
    extracted_text = cv2.bitwise_and(image, mask)
    
    # 将抠出的文字转换为灰度图像
    extracted_gray = cv2.cvtColor(extracted_text, cv2.COLOR_BGR2GRAY)
    
    # 对抠出的文字图像进行二值化
    _, thresh = cv2.threshold(extracted_gray, 0, 255, cv2.THRESH_BINARY)
    
    # 找到文字区域的轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 创建一个与原图大小相同的黑色背景
    filled_text = np.zeros_like(image)
    
    # 遍历每个轮廓，填充文字内部的黑色，并忽略小面积的图像部分
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area_threshold:
            cv2.drawContours(filled_text, [contour], 0, (0, 0, 0), cv2.FILLED)
    
    # 将填充后的文字图像与抠出的文字图像进行合并
    merged_text = cv2.bitwise_or(extracted_text, filled_text)
    
    # 将合并后的文字图像转换为透明背景的 PNG 图像
    bgra = cv2.cvtColor(merged_text, cv2.COLOR_BGR2BGRA)
    bgra[:, :, 3] = np.where(bgra[:, :, 0] == 0, 0, 255)
    
    return bgra

# 获取当前路径下的所有图片文件
current_path = os.path.dirname(os.path.abspath(__file__))
image_files = [file for file in os.listdir(current_path) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

# 遍历每个图片文件，识别并抠出文字部分，保存为透明背景的PNG图片
for image_file in image_files:
    image_path = os.path.join(current_path, image_file)
    try:
        extracted_text = extract_text(image_path, min_area_threshold=10)
        output_path = os.path.splitext(image_file)[0] + '_extracted.png'
        cv2.imwrite(output_path, extracted_text)
        print(f"Extracted text from {image_file} and saved as {output_path}")
    except Exception as e:
        print(f"Error processing {image_file}: {str(e)}")