import pandas as pd
import glob

# 获取当前路径下所有 xlsx 文件的文件名
file_list = glob.glob("*.xlsx")

# 读取第一个文件，作为合并的基础 DataFrame
combined_df = pd.read_excel(file_list[0])

# 循环读取其他文件，按照第一列 Symbol 进行合并
for file in file_list[1:]:
    df = pd.read_excel(file)
    combined_df = pd.merge(combined_df, df, on='Symbol', how='inner')

# 去除重合公司名称不匹配的行后，拼接所有相同 Symbol 的行
combined_df = combined_df.drop_duplicates(subset=['Symbol'])

# 保存最终合并后的结果为一个新文件
combined_df.to_excel("combined_sp500_esg.xlsx", index=False)

print("合并完成，结果已保存为 combined_sp500_esg.xlsx 文件。")
