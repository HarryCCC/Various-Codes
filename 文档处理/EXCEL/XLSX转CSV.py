import pandas as pd
import os
from tqdm import tqdm

def convert_xlsx_to_csv(xlsx_filename):
    # 读取 XLSX 文件
    print(f'正在读取 {xlsx_filename}...')
    df = pd.read_excel(xlsx_filename)
    
    # 构造 CSV 文件名
    csv_filename = os.path.splitext(xlsx_filename)[0] + '.csv'
    
    # 设置写入 CSV 文件的块大小
    chunksize = 1000
    num_chunks = len(df) // chunksize + 1
    
    print(f'正在转换 {xlsx_filename} 为 {csv_filename}...')
    
    with tqdm(total=len(df), desc='转换进度') as pbar:
        # 以写模式打开 CSV 文件，并写入第一块数据（包括列名）
        df.iloc[:chunksize].to_csv(csv_filename, index=False)
        pbar.update(chunksize)
        
        # 追加模式写入剩余的数据块
        for i in range(1, num_chunks):
            start_row = i * chunksize
            end_row = (i + 1) * chunksize
            df.iloc[start_row:end_row].to_csv(csv_filename, mode='a', header=False, index=False)
            pbar.update(chunksize)
    
    print(f'文件 {xlsx_filename} 已成功转换为 {csv_filename}')

# 使用示例
convert_xlsx_to_csv('5.股价对齐数据-原始数据.xlsx')
