import os

# 获取当前目录路径
current_dir = os.getcwd()

# 获取当前目录下所有的PDF文件
pdf_files = [file for file in os.listdir(current_dir) if file.endswith('.pdf')]

# 按照文件名称排序
pdf_files.sort()

# 遍历PDF文件列表，对每个文件进行重命名
for i, file in enumerate(pdf_files, start=1):
    # 构建新的文件名
    new_file_name = f"{i}-{file}"
    
    # 获取文件的完整路径
    old_file_path = os.path.join(current_dir, file)
    new_file_path = os.path.join(current_dir, new_file_name)
    
    # 重命名文件
    os.rename(old_file_path, new_file_path)
    
    print(f"重命名完成：{file} -> {new_file_name}")

print("所有PDF文件重命名完成！")