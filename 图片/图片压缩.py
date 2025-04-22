import os
from PIL import Image

def compress_image(input_path, output_path, quality=85):
    """
    压缩指定路径的图片，并保存到新路径。

    参数:
    input_path (str): 输入图片的文件路径。
    output_path (str): 压缩后图片保存的文件路径。
    quality (int): 压缩质量，范围通常是 1-95。
                     数值越低，压缩率越高，文件越小，但质量损失越大。
                     数值越高，压缩率越低，文件越大，但质量越好。
                     建议值通常在 75 到 95 之间。
    """
    try:
        # 打开图片
        with Image.open(input_path) as img:
            # 确保输出目录存在 (如果输出路径包含目录)
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"创建目录: {output_dir}")

            # 保存图片，指定格式为 JPEG 并设置质量
            # optimize=True 尝试进一步优化文件大小
            # progressive=True 对某些查看器可能有更好的加载体验，但非必须
            img.save(output_path, "JPEG", quality=quality, optimize=True) # progressive=True)

            original_size = os.path.getsize(input_path) / 1024  # KB
            compressed_size = os.path.getsize(output_path) / 1024 # KB

            print(f"图片压缩成功!")
            print(f"  原始文件: {input_path} ({original_size:.2f} KB)")
            print(f"  压缩文件: {output_path} ({compressed_size:.2f} KB)")
            print(f"  压缩质量: {quality}")
            print(f"  压缩比率: {compressed_size / original_size * 100:.2f}% (大小)")

    except FileNotFoundError:
        print(f"错误: 输入文件未找到 -> {input_path}")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")

# --- 配置区域 ---
input_image_name = "123.jpg"
output_image_name = "123_compressed.jpg" # 可以自定义输出文件名
compression_quality = 23  # 在这里设置你想要的压缩质量 (例如 75)

# 获取当前脚本所在的目录
current_directory = os.getcwd() # 或者使用 os.path.dirname(__file__) 如果在脚本中运行

# 构建完整的文件路径
input_file_path = os.path.join(current_directory, input_image_name)
output_file_path = os.path.join(current_directory, output_image_name)

# --- 执行压缩 ---
compress_image(input_file_path, output_file_path, quality=compression_quality)