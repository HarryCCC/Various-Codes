import os
import pandas as pd

def extract_excel_previews(input_dir: str, output_file: str, preview_rows: int = 5):
    """
    遍历指定目录下的所有Excel文件，提取每个文件的前几行并保存到TXT文件中。

    :param input_dir: 包含Excel文件的目标文件夹路径
    :param output_file: 输出TXT文件的完整路径
    :param preview_rows: 需要提取的前N行，默认为5行
    """
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误：找不到指定的目录 '{input_dir}'")
        return

    # 获取目录下所有的 .xlsx 或 .xls 文件
    excel_files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls'))]
    
    if not excel_files:
        print(f"提示：在 '{input_dir}' 目录下未找到任何Excel文件。")
        return

    print(f"共发现 {len(excel_files)} 个Excel文件，开始提取预览数据...")

    # 以 UTF-8 编码打开目标TXT文件，防止中文乱码
    with open(output_file, 'w', encoding='utf-8') as txt_file:
        # 写入全局标题
        txt_file.write(f"=== 文件夹 [{os.path.basename(input_dir) or input_dir}] 表格预览汇总 ===\n")
        txt_file.write(f"提取规则：每个表格前 {preview_rows} 行\n\n")

        for index, filename in enumerate(excel_files, start=1):
            file_path = os.path.join(input_dir, filename)
            print(f"正在处理 ({index}/{len(excel_files)}): {filename}")
            
            # 写入文件分隔头
            txt_file.write("=" * 60 + "\n")
            txt_file.write(f"【文件 {index}】: {filename}\n")
            txt_file.write("-" * 60 + "\n")
            
            try:
                # 核心逻辑：使用 nrows 参数仅读取前 N 行，极大提升大文件处理效率
                # engine='openpyxl' 用于确保 .xlsx 格式被正确解析
                df = pd.read_excel(file_path, nrows=preview_rows, engine='openpyxl')
                
                if df.empty:
                    txt_file.write("[提示] 该表格为空或无数据行。\n")
                else:
                    # 将 DataFrame 转换为格式化的字符串并写入TXT
                    # index=False 表示不在TXT中输出行号索引（0, 1, 2...）
                    txt_file.write(df.to_string(index=False))
                    txt_file.write("\n")
            
            except Exception as e:
                txt_file.write(f"[错误] 读取文件失败，原因: {str(e)}\n")
            
            # 每个文件数据结尾预留空行，确保排版清晰
            txt_file.write("\n\n")

    print(f"\n✅ 提取完成！所有预览数据已成功保存至：{output_file}")

if __name__ == "__main__":
    # ================= 配置区域 =================
    # 1. 设置包含Excel文件的文件夹路径 (如果是当前目录，可以使用 '.')
    # 例如 Windows 路径: r"D:\Data\IronOreData"
    TARGET_DIRECTORY = "." 
    
    # 2. 设置输出TXT文件的名称与路径
    OUTPUT_TXT_NAME = "excel_previews_combined.txt"
    
    # 3. 设置需要提取的行数（包含表头后，正文的行数）
    ROWS_TO_EXTRACT = 15
    # ============================================

    extract_excel_previews(
        input_dir=TARGET_DIRECTORY, 
        output_file=OUTPUT_TXT_NAME, 
        preview_rows=ROWS_TO_EXTRACT
    )