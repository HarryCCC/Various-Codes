import os
import zipfile
import shutil

def compress_folder(input_folder, output_file, compression_level):
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        raise ValueError(f"输入文件夹 {input_folder} 不存在")
    
    # 压缩等级转换：从0（不压缩）到9（最高压缩）
    compression_level = max(0, min(compression_level, 9))  # 确保压缩等级在0到9之间

    # 创建临时压缩文件
    shutil.make_archive(output_file, 'zip', input_folder)

    # 重新打开压缩文件并调整压缩级别
    temp_zip = output_file + '.zip'
    final_zip = output_file + '_compressed.zip'

    with zipfile.ZipFile(temp_zip, 'r') as temp_zipfile:
        with zipfile.ZipFile(final_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as final_zipfile:
            for item in temp_zipfile.infolist():
                buffer = temp_zipfile.read(item.filename)
                final_zipfile.writestr(item, buffer)
    
    # 删除临时压缩文件
    os.remove(temp_zip)

if __name__ == "__main__":
    input_folder = "input"  # 替换为实际的输入文件夹路径
    output_file = "output"  # 替换为实际的输出文件路径，不包括扩展名
    compression_level = 9   # 替换为所需的压缩级别（0到9）

    compress_folder(input_folder, output_file, compression_level)
