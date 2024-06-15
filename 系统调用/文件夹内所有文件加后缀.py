import os

def add_suffix_to_files(folder_path, suffix=".docx"):
    # 检查给定路径是否为有效目录
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 构造文件的完整路径
        file_path = os.path.join(folder_path, filename)
        
        # 如果是文件而不是文件夹
        if os.path.isfile(file_path):
            # 构造新的文件名
            new_filename = filename + suffix
            new_file_path = os.path.join(folder_path, new_filename)
            
            # 重命名文件
            os.rename(file_path, new_file_path)
            print(f"Renamed: {filename} to {new_filename}")

# 设置目标文件夹路径
folder_path = "./123"

# 调用函数执行文件重命名操作
add_suffix_to_files(folder_path)
