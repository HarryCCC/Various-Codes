import os

def list_file_types(directory):
    # 存储文件扩展名的集合
    file_types = set()
    
    # 遍历目录及其子目录中的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext:  # 确保扩展名非空
                file_types.add(ext)
    
    return file_types

def count_selected_files_characters(directory, script_types, note_types, data_types):
    # 初始化字符计数
    total_script_chars = 0
    total_note_chars = 0
    total_data_chars = 0
    
    # 遍历目录及其子目录中的所有文件
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            filepath = os.path.join(root, file)
            # 检查文件类型并读取字符数
            try:
                if ext in script_types or ext in note_types or ext in data_types:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if ext in script_types:
                            total_script_chars += len(content)
                        elif ext in note_types:
                            total_note_chars += len(content)
                        elif ext in data_types:
                            total_data_chars += len(content)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return total_script_chars, total_note_chars, total_data_chars

# 文件类型分类
script_types = {'.r', '.py', '.sh', '.pyw', '.bat', '.html'}
note_types = {'.md', '.txt'}
data_types = {'.csv', '.xls', '.xlsx', '.sample'}

# 用法示例
directory_path = r'C:\Users\11470\Desktop\HARISAN\Various-Codes'
file_types = list_file_types(directory_path)
print(f"Found file types: {file_types}")

# 计算字符数
total_script_chars, total_note_chars, total_data_chars = count_selected_files_characters(directory_path, script_types, note_types, data_types)
print(f"Total characters in script files: {total_script_chars}")
print(f"Total characters in note files: {total_note_chars}")
print(f"Total characters in data files: {total_data_chars}")
