# -*- coding: utf-8 -*-

"""
一个用于查找目录下内容高度相似图片的工具。
版本: 1.0
功能:
- 递归扫描指定目录下的所有图片。
- 使用感知哈希(pHash)算法计算每张图片的“指纹”。
- 通过比较指纹间的汉明距离来判断相似度。
- 将高度相似的图片分组并输出文件名。
"""

import os
import argparse
from PIL import Image
from tqdm import tqdm

try:
    import imagehash
except ImportError:
    print("错误: 缺少 'imagehash' 库。请运行 'pip install imagehash' 进行安装。")
    exit(1)

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORTED = True
except ImportError:
    HEIF_SUPPORTED = False

# --- 可调参数 ---
# 相似度阈值。汉明距离越小，代表图片越相似。
# 0:      几乎是完全相同的图片。
# 1-5:    非常相似 (轻微缩放、水印、格式转换)。
# 6-10:   有些相似 (可能经过裁剪或颜色调整)。
# 推荐使用 5 或以下的值来查找重复图片。
SIMILARITY_THRESHOLD = 5

# 支持的图片文件扩展名 (小写)
SUPPORTED_EXTENSIONS = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')

def compute_hashes(directory: str) -> dict:
    """
    计算目录中所有图片的感知哈希值。
    
    :param directory: 要扫描的根目录。
    :return: 一个字典，键是图片路径，值是其哈希对象。
    """
    hashes = {}
    image_files = []
    # 1. 递归查找所有支持的图片文件
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(os.path.join(root, file))

    if not image_files:
        return {}
        
    print(f"找到 {len(image_files)} 张图片，开始计算哈希值...")
    
    # 2. 为每张图片计算哈希值，并显示进度条
    for filepath in tqdm(image_files, desc="计算哈希", unit="张"):
        try:
            with Image.open(filepath) as img:
                # 使用pHash算法，对内容变化鲁棒性好
                h = imagehash.phash(img)
                hashes[filepath] = h
        except Exception as e:
            print(f"\n警告：无法处理文件 '{os.path.basename(filepath)}'，已跳过。原因: {e}")
            
    return hashes

def find_similar_images(hashes: dict, threshold: int) -> list:
    """
    根据哈希值查找相似的图片组。
    
    :param hashes: 包含所有图片哈希值的字典。
    :param threshold: 相似度阈值（汉明距离）。
    :return: 一个列表，其中每个元素是是一个包含相似图片路径的列表。
    """
    similar_groups = []
    processed_files = set()
    
    # 将字典的键（文件名）转换为列表以便索引
    filenames = list(hashes.keys())
    
    if not filenames:
        return []

    print("\n正在比较图片相似度...")
    
    # 使用tqdm创建外层循环的进度条
    for i in tqdm(range(len(filenames)), desc="比较进度", unit="张"):
        f1 = filenames[i]
        if f1 in processed_files:
            continue
        
        current_group = [f1]
        # 内层循环从 i+1 开始，避免重复比较和自己跟自己比
        for j in range(i + 1, len(filenames)):
            f2 = filenames[j]
            if f2 in processed_files:
                continue
            
            # 计算两个哈希值之间的汉明距离
            distance = hashes[f1] - hashes[f2]
            
            if distance <= threshold:
                current_group.append(f2)
        
        if len(current_group) > 1:
            similar_groups.append(current_group)
            # 将已分组的文件标记为已处理
            for item in current_group:
                processed_files.add(item)
                
    return similar_groups

def main():
    """主执行函数"""
    parser = argparse.ArgumentParser(description="查找目录下的高度相似图片。")
    parser.add_argument(
        "directory", 
        nargs='?', 
        default='.', 
        help="要扫描的图片目录 (默认为当前目录)。"
    )
    parser.add_argument(
        "-t", "--threshold", 
        type=int, 
        default=SIMILARITY_THRESHOLD,
        help=f"相似度阈值 (0-10), 越小越相似 (默认: {SIMILARITY_THRESHOLD})。"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在。")
        return

    # 1. 计算哈希
    hashes = compute_hashes(args.directory)
    if not hashes:
        print("在指定目录中未找到任何图片。")
        return

    # 2. 查找相似组
    similar_groups = find_similar_images(hashes, args.threshold)
    
    # 3. 输出结果
    print("-" * 40)
    if not similar_groups:
        print(f"🎉 扫描完成！在阈值为 {args.threshold} 的标准下，未发现相似的图片。")
    else:
        print(f"✅ 扫描完成！共找到 {len(similar_groups)} 组相似图片：\n")
        for i, group in enumerate(similar_groups, 1):
            print(f"--- 相似组 {i} ---")
            for filename in group:
                print(f"  - {filename}")
            print() # 增加一个空行以分隔组

if __name__ == "__main__":
    main()