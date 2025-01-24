import os
import csv
from openpyxl import Workbook

def extract_csv_data():
    extracted_data = []
    error_log = []

    for root, dirs, files in os.walk('.'):
        for filename in files:
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(root, filename)
                processed = False
                
                encodings = ['utf-8-sig', 'gb18030', 'gbk', 'big5', 'utf-16', 'latin-1']
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as csv_file:
                            try:
                                dialect = csv.Sniffer().sniff(csv_file.read(1024))
                                csv_file.seek(0)
                            except:
                                dialect = csv.excel
                            
                            reader = csv.reader(csv_file, dialect=dialect)
                            for row in reader:
                                if row and row[0].strip().upper() == 'IF2503':
                                    if len(row) >= 6:
                                        # 添加文件名、成交量、成交金额
                                        extracted_data.append((
                                            filename,         # 文件名
                                            row[4].strip(),   # 成交量
                                            row[5].strip()    # 成交金额
                                        ))
                                    else:
                                        error_log.append(f"列不足 | {filename}")
                                    processed = True
                                    break
                            if processed:
                                break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        error_log.append(f"处理失败 | {filename} | {str(e)}")
                        continue
                
                if not processed:
                    error_log.append(f"编码问题 | {filename}")

    # 保存结果
    if extracted_data:
        wb = Workbook()
        ws = wb.active
        # 添加三列标题
        ws.append(['文件名', '成交量', '成交金额'])
        
        for record in extracted_data:
            ws.append(list(record))
        
        wb.save('提取结果.xlsx')
        print(f"成功提取 {len(extracted_data)} 条数据")
    else:
        print("未找到有效数据")

    # 输出错误日志
    if error_log:
        with open("处理日志.txt", "w", encoding="utf-8") as log:
            log.write("\n".join(error_log))
        print(f"发现 {len(error_log)} 个问题，详见处理日志.txt")

if __name__ == "__main__":
    extract_csv_data()