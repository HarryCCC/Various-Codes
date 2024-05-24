import os

# 获取当前目录下所有文件（不包括子文件夹）
files = [f for f in os.listdir('.') if os.path.isfile(f)]

# 移除文件后缀
files_without_extension = [os.path.splitext(f)[0] for f in files]

# 将文件名用单引号括起来并用逗号连接
files_str = ', '.join(f"'{file}'" for file in files_without_extension)

# 将结果写入txt文件
with open('文件名汇总.txt', 'w') as output_file:
    output_file.write(files_str)

print("文件名已成功写入文件名汇总.txt")
