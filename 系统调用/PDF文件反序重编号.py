import os
import re
import shutil

def rename_pdf_files_reverse(directory):
    # 匹配PDF文件的正则表达式
    pdf_pattern = re.compile(r'.*\.pdf$')
    
    # 获取当前目录下所有的文件名
    files = os.listdir(directory)
    
    # 过滤出PDF文件并按名称反向自然排序
    pdf_files = sorted(filter(lambda f: pdf_pattern.match(f), files), reverse=True)
    
    # 重新编号PDF文件
    for index, filename in enumerate(pdf_files, start=132):
        # 构建新的文件名
        new_filename = f"{index}.pdf"
        old_file_path = os.path.join(directory, filename)
        new_file_path = os.path.join(directory, new_filename)
        
        # 重命名文件
        print(f"Renaming '{filename}' to '{new_filename}'")
        shutil.move(old_file_path, new_file_path)

# 调用函数，传入当前脚本所在的目录
rename_pdf_files_reverse(os.path.dirname(os.path.abspath(__file__)))