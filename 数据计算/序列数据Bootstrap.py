import pandas as pd
import numpy as np

# 读取整个Excel文件
df = pd.read_excel('FINM3008 - Assignment Data Analysis S1 2024.xlsx', sheet_name='Yearly Returns', index_col=0)

# 获取资产类别名称
asset_classes = df.iloc[0].tolist()

# 删除前两行
df = df.iloc[2:]

# 设置bootstrap参数
n_boot = 1000
sample_length = len(df)

# 定义一个函数来计算统计量
def calculate_stats(data):
    # 将非数值类型转换为NaN
    data = pd.to_numeric(data, errors='coerce')
    return {'mean': data.mean(), 'std': data.std(), 'min': data.min(), 'max': data.max(), 'median': data.median()}

# 初始化一个字典来存储结果
results = {col: {'mean': [], 'std': [], 'min': [], 'max': [], 'median': []} for col in df.columns}

# 进行bootstrapping
for i in range(n_boot):
    sample = df.sample(n=sample_length, replace=True)
    for col in df.columns:
        stats = calculate_stats(sample[col])
        for key, value in stats.items():
            results[col][key].append(value)

# 将结果转换为DataFrame
boot_df = pd.DataFrame(results)

# 计算置信区间和确定值
output = {}
for col in df.columns:
    asset_class = asset_classes[df.columns.get_loc(col)]
    output[asset_class] = {
        'mean': {'value': df[col].mean(),'ci': np.percentile(boot_df[col]['mean'], [2.5, 97.5])},
        'std': {'value': df[col].std(), 'ci': np.percentile(boot_df[col]['std'], [2.5, 97.5]) },
        'min': {'value': df[col].min()},
        'max': {'value': df[col].max()},
        'median': {'value': df[col].median()}
    }

# 打印结果
for asset_class, stats in output.items():
    print(f"{asset_class}:")
    for stat, values in stats.items():
        if 'ci' in values:
            print(f" {stat.capitalize()} Value: {values['value']}, 95% CI: {values['ci']} ")
        else:
            print(f" {stat.capitalize()}: {values['value']}")

# 输出每一列数据的bootstrap的mean和std值的列表
print("\nBootstrap Mean Values:")
print(" ".join([f"{output[asset_class]['mean']['value']}" for asset_class in asset_classes]))

print("\nBootstrap Std Values:")
print(" ".join([f"{output[asset_class]['std']['value']}" for asset_class in asset_classes]))