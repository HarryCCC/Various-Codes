import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError # 导入特定的错误类型

def scan_pdfs_recursive_and_display_tree(root_folder_name="HYT-荷兰-申根签-资料"):
    """
    递归扫描指定根文件夹及其所有子文件夹中的PDF文件，
    以树状结构显示，并统计总文件数和总页数。

    参数:
    root_folder_name (str): 相对于当前工作目录的根文件夹名称。

    返回:
    tuple: (grand_total_pdf_count, grand_total_pages)
           如果根文件夹不存在，则返回 (0, 0)
    """
    grand_total_pdf_count = 0
    grand_total_pages = 0

    current_working_directory = os.getcwd()
    start_path = os.path.join(current_working_directory, root_folder_name)

    if not os.path.isdir(start_path):
        print(f"错误：根文件夹 '{start_path}' 不存在。")
        return 0, 0

    print(f"开始扫描文件夹: {root_folder_name}\n--- 文件夹与PDF结构 ---")

    # 记录已经打印过的父目录，避免重复打印
    # os.walk 本身会按顺序遍历，这里主要是为了美化输出根目录名称
    # 我们可以直接使用 start_path 作为初始打印

    # 获取基础缩进的参考路径长度，用于计算相对深度
    # 加1是为了让根目录下的文件也有基础缩进
    # base_path_len = len(os.path.abspath(start_path).split(os.sep)) -1
    # 或者更简单的方式是计算从 start_path 开始的深度

    for dirpath, dirnames, filenames in os.walk(start_path):
        # 计算当前目录相对于起始扫描目录的深度
        # os.path.relpath 获取相对路径
        relative_path = os.path.relpath(dirpath, start_path)
        if relative_path == ".": # 当前是根目录
            depth = 0
            # 打印根目录名称
            print(f"{root_folder_name}/")
        else:
            depth = len(relative_path.split(os.sep))
            # 打印子目录名称
            indent = "    " * depth
            print(f"{indent}{os.path.basename(dirpath)}/")


        # 文件处理的缩进应该比其所在目录多一级
        file_indent = "    " * (depth + 1)
        
        current_folder_pdf_count = 0
        current_folder_pages = 0

        # 对文件名进行排序，使其输出更稳定有序
        sorted_filenames = sorted(filenames)

        for filename in sorted_filenames:
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, "rb") as f:
                        reader = PdfReader(f)
                        num_pages = len(reader.pages)
                        
                        print(f"{file_indent}📄 {filename} ({num_pages} 页)")
                        
                        grand_total_pdf_count += 1
                        grand_total_pages += num_pages
                        current_folder_pdf_count +=1
                        current_folder_pages += num_pages
                except PdfReadError as e:
                    print(f"{file_indent}📄 {filename} (无法读取: {e})")
                except Exception as e:
                    print(f"{file_indent}📄 {filename} (处理错误: {e})")
        
        # (可选) 打印当前文件夹的PDF统计小结
        # if current_folder_pdf_count > 0:
        #     print(f"{file_indent}└─ 小计: {current_folder_pdf_count} 个PDF, {current_folder_pages} 页")


    return grand_total_pdf_count, grand_total_pages

if __name__ == "__main__":
    folder_to_scan = "HYT-荷兰-申根签-资料"
    total_pdfs, total_pages = scan_pdfs_recursive_and_display_tree(folder_to_scan)

    print("\n--- 扫描完成 ---")
    print("--- 总体统计结果 ---")
    print(f"在文件夹 '{folder_to_scan}' 及其所有子文件夹中:")
    print(f"  共扫描到 PDF 文件总数: {total_pdfs} 个")
    print(f"  所有 PDF 文件总页数: {total_pages} 页")