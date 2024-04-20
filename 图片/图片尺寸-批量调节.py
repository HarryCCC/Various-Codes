from PIL import Image
import os

def resize_images_in_folder(folder_path, size):
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            with Image.open(image_path) as img:
                img = img.resize(size, Image.LANCZOS)
                img.save(image_path)

# 示例
resize_images_in_folder('C:/Users/11470/Desktop', (500, 500))
