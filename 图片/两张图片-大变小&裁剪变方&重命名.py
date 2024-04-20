from PIL import Image
import os

def resize_and_crop_image(folder_path):
    images = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.png'):
            image_path = os.path.join(folder_path, filename)
            img = Image.open(image_path)
            images.append((img, image_path))
    if len(images) != 2:
        print("Error: There should be exactly 2 images in the folder")
        return
    # Find the smaller image
    smaller_image, smaller_image_path = min(images, key=lambda x: max(x[0].size))
    larger_image, larger_image_path = max(images, key=lambda x: max(x[0].size))
    # Find the length of the longest side of the smaller image
    smaller_image_longest_side = max(smaller_image.size)
    # Resize the larger image
    larger_image_ratio = larger_image.size[0] / larger_image.size[1]
    if larger_image_ratio > 1:
        new_size = (int(smaller_image_longest_side * larger_image_ratio), smaller_image_longest_side)
    else:
        new_size = (smaller_image_longest_side, int(smaller_image_longest_side / larger_image_ratio))
    larger_image = larger_image.resize(new_size, Image.LANCZOS)
    # Crop the larger image
    left = 0
    top = 0
    right = smaller_image_longest_side
    bottom = smaller_image_longest_side
    larger_image = larger_image.crop((left, top, right, bottom))
    
    # Save the modified image before renaming
    larger_image.save(larger_image_path)
    
    # Close the images before renaming
    smaller_image.close()
    
    # Save the modified image
    base_name, ext = os.path.splitext(smaller_image_path)
    temp_smaller_image_path = base_name + '_origin' + ext
    os.rename(smaller_image_path, temp_smaller_image_path)
    os.rename(larger_image_path, smaller_image_path)


# 示例
resize_and_crop_image('C:/Users/11470/Desktop')
