import pandas as pd

def sort_sheets(file_path):
    # 读取Excel文件
    xls = pd.ExcelFile(file_path)
    
    # 获取所有sheet的名称并排序
    sorted_sheet_names = sorted(xls.sheet_names)
    
    # 创建一个字典来存储所有的sheet数据
    sheets_dict = {}

    # 遍历排序后的sheet名称，读取数据并存储到字典中
    for sheet_name in sorted_sheet_names:
        sheets_dict[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
    
    # 定义新的文件名称
    new_file_path = file_path.replace('.xlsx', '_sorted.xlsx')
    
    # 创建一个新的ExcelWriter对象
    with pd.ExcelWriter(new_file_path, engine='openpyxl') as writer:
        for sheet_name, df in sheets_dict.items():
            # 保留条件格式和原始数据格式
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"排序后的Excel文件已保存为: {new_file_path}")

# 调用函数
file_path = "细分因子回测结果_大盘成长.xlsx"
sort_sheets(file_path)
