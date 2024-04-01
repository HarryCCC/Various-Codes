import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 读取Excel文件
df = pd.read_excel('metric.xlsx', header=1)

# 将数据转换为适当的格式
techniques = df.columns[1:33].tolist()
metrics = df.columns[33:].tolist()
paper_counts = df.iloc[:, 1:33].apply(lambda x: x.str.contains('Y')).sum()

# 创建一个新的DataFrame来存储每个metric和technique的paper数量
heatmap_data = pd.DataFrame(0, index=metrics, columns=techniques)

for metric in metrics:
    for technique in techniques:
        count = ((df[metric] == 'Y') & (df[technique] == 'Y')).sum()
        heatmap_data.at[metric, technique] = count

# 设置图形大小
plt.figure(figsize=(15, 8))

# 生成热力图
sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='d', cbar_kws={'label': 'Number of Papers'})

# 设置标题和标签
plt.title('Heatmap between Technique and Metric', fontsize=18, fontweight='bold')
plt.xlabel('Techniques', fontsize=14, fontweight='bold')
plt.ylabel('Metrics', fontsize=14, fontweight='bold')

# 调整横轴标签的字体大小和旋转角度
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=12)

# 自动调整子图参数,使标签完全可见
plt.tight_layout()

# 显示图形
plt.show()