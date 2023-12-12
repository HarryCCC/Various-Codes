import os
import subprocess

def open_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # 在Windows上使用os.startfile
                if os.name == 'nt':
                    os.startfile(file_path)
                # 在Unix-like系统上使用subprocess
                else:
                    subprocess.call(('xdg-open', file_path))
            except Exception as e:
                print(f"无法打开文件 {file_path}: {e}")

# 调用函数并传入文件夹路径
folder_path = r"C:\Users\11470\Documents\WPSDrive\715723823_3\WPS云盘\ANU\ECON3102" 
open_files_in_folder(folder_path)
