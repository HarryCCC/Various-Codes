import pandas as pd
import os

# --- 配置 ---
# 输入文件名列表
input_files = [
    '申请的绿色发明专利的被引用数量_1.xlsx',
    '申请的绿色发明专利的被引用数量_2.xlsx'
]
# 输出文件名
output_file = '申请的绿色发明专利的被引用数量.xlsx'
# ----------------

# 获取当前工作目录
current_directory = os.getcwd()
print(f"当前工作目录: {current_directory}")

# 存储所有读取到的 DataFrame
all_dataframes = []
files_found = True

# --- 读取文件 ---
print("开始读取 Excel 文件...")
for file_name in input_files:
    file_path = os.path.join(current_directory, file_name)
    if os.path.exists(file_path):
        try:
            print(f"正在读取: {file_name}")
            # 读取 Excel 文件，假设数据在第一个 sheet
            df = pd.read_excel(file_path, engine='openpyxl')
            all_dataframes.append(df)
            print(f"成功读取: {file_name}，包含 {len(df)} 行数据")
        except FileNotFoundError:
            print(f"错误: 文件未找到 - {file_path}")
            files_found = False
            break # 如果一个文件找不到，则停止处理
        except Exception as e:
            print(f"读取文件 {file_name} 时发生错误: {e}")
            files_found = False
            break # 如果读取出错，则停止处理
    else:
        print(f"错误: 文件不存在于当前目录下 - {file_name}")
        files_found = False
        break # 如果一个文件找不到，则停止处理


# --- 合并与写入 ---
if files_found and all_dataframes:
    print("\n开始合并数据...")
    try:
        # 纵向合并 (沿着行的方向，即 axis=0)
        # ignore_index=True 会重新生成从 0 开始的连续索引
        combined_df = pd.concat(all_dataframes, ignore_index=True, axis=0)
        print(f"合并完成，总共包含 {len(combined_df)} 行数据")

        # 构建输出文件的完整路径
        output_path = os.path.join(current_directory, output_file)

        print(f"\n开始将合并后的数据写入到: {output_file} ...")
        # 将合并后的 DataFrame 写入新的 Excel 文件
        # index=False 表示不将 DataFrame 的索引写入 Excel 文件中
        combined_df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"成功！合并后的文件已保存为: {output_path}")

    except Exception as e:
        print(f"在合并或写入文件时发生错误: {e}")
elif not files_found:
    print("\n由于部分或全部输入文件未找到或读取错误，无法进行合并。")
else:
    print("\n未能读取到任何数据，无法进行合并。")