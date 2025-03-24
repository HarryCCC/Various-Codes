import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# 参数库 - 集中管理图表视觉元素设置
PARAMS = {
    # 字体大小设置
    'title_fontsize': 24,         # 主标题字体大小
    'subtitle_fontsize': 20,      # 子图标题字体大小
    'suptitle_fontsize': 26,      # 总标题字体大小
    'axis_label_fontsize': 18,    # 坐标轴标签字体大小
    'tick_fontsize': 16,          # 刻度标签字体大小
    'legend_fontsize': 20,        # 图例字体大小
    'annotation_fontsize': 16,    # 标注文字字体大小
    'data_label_fontsize': 16,    # 数据标签字体大小
    
    # 线条和标记设置
    'linewidth': 4,               # 线条宽度
    'markersize': 10,             # 标记大小
    'grid_alpha': 0.7,            # 网格透明度
    'bar_width': 0.7,             # 柱状图宽度
    'bar_alpha': 0.8,             # 柱状图透明度
    
    # 图例设置
    'legend_linewidth': 2,        # 图例边框线宽
    'legend_loc': 'upper left',   # 图例位置
    
    # 字体样式
    'fontweight': 'bold',         # 字体粗细
    
    # 颜色设置
    'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],  # 主要颜色
}

# 设置中文字体，根据系统可用字体选择一个
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['legend.handlelength'] = 3  # 增加图例中线条长度
plt.rcParams['legend.handleheight'] = 1.5  # 增加图例中线条高度
plt.rcParams['legend.handletextpad'] = 0.8  # 增加图例标记与文本间距
plt.rcParams['legend.borderpad'] = 1.0  # 增加图例内边距
plt.rcParams['legend.frameon'] = True  # 显示图例边框
plt.rcParams['legend.edgecolor'] = '0.8'  # 设置图例边框颜色

# 创建标准的图例字体设置函数
def set_legend_style(legend_obj):
    """设置图例样式的统一函数"""
    legend_obj.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    for text in legend_obj.get_texts():
        text.set_fontsize(PARAMS['legend_fontsize'])
        text.set_fontweight(PARAMS['fontweight'])
    return legend_obj

# 定义共通的年份数据
years = [2025, 2026, 2027, 2028, 2029]

# 1. 主要财务指标增长趋势图
def plot_financial_indicators():
    plt.figure(figsize=(11, 7))
    
    revenue = [1.5, 5.8, 18.4, 42.7, 76.5]
    gross_profit = [0.6, 2.6, 9.2, 23.5, 45.9]
    net_profit = [-0.5, 0.1, 2.4, 10.7, 26.8]
    
    # 增加线条粗细和标记大小
    plt.plot(years, revenue, 'o-', color=PARAMS['colors'][0], 
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
             label='收入/Revenue')
    plt.plot(years, gross_profit, 's-', color=PARAMS['colors'][2], 
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
             label='毛利/Gross Profit')
    plt.plot(years, net_profit, '^-', color=PARAMS['colors'][3], 
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
             label='净利润/Net Profit')
    
    # 标记盈亏平衡点
    plt.axvline(x=2026, color='purple', linestyle='--', linewidth=3, alpha=0.7)
    plt.annotate('Break-even', xy=(2026, 25), xytext=(2026.2, 30),
                arrowprops=dict(facecolor='purple', shrink=0.05, width=2),
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('金额 (百万美元)/Amount (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('主要财务指标增长趋势/Financial Growth Indicators', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    
    # 使用FontProperties对象设置图例样式
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    plt.ylim(-2, 80)
    
    # 修正x轴标签为整数年份，并增加字体大小
    plt.xticks(years, [str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    
    plt.tight_layout()
    plt.show()

# 2. 毛利率和净利润率变化图
def plot_margin_trends():
    plt.figure(figsize=(11, 7))
    
    gross_margin = [40, 45, 50, 55, 60]
    net_margin = [-30, 2, 13, 25, 35]
    
    bar_width = 0.35
    index = np.arange(len(years))
    
    # 增加条形图宽度
    bars1 = plt.bar(index, gross_margin, bar_width, color=PARAMS['colors'][2], 
                    alpha=PARAMS['bar_alpha'], label='毛利率/Gross Margin')
    bars2 = plt.bar(index + bar_width, net_margin, bar_width, color=PARAMS['colors'][3], 
                    alpha=PARAMS['bar_alpha'], label='净利润率/Net Margin')
    
    # 添加数据标签，增加字体大小
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%', ha='center', va='bottom', 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
                
    for bar in bars2:
        height = bar.get_height()
        if height < 0:
            ypos = height - 2
            va = 'top'
        else:
            ypos = height + 1
            va = 'bottom'
        plt.text(bar.get_x() + bar.get_width()/2., ypos,
                f'{height}%', ha='center', va=va, 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('百分比/Percentage (%)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('毛利率与净利润率预测/Margin Projections', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    plt.xticks(index + bar_width / 2, years, fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 使用FontProperties对象设置图例样式
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    plt.ylim(-35, 65)
    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'], axis='y')
    
    plt.tight_layout()
    plt.show()

# 3. 产品线收入构成演变图
def plot_product_revenue():
    plt.figure(figsize=(11, 7))
    
    products = ['SeaFilm', 'SeaBox', 'SeaBag', 'SeaCush', '技术授权/Tech License']
    data = np.array([
        [0.8, 2.8, 7.4, 15.4, 23.7],  # SeaFilm
        [0.5, 1.7, 5.5, 12.8, 22.1],  # SeaBox
        [0.2, 0.9, 3.5, 8.5, 15.3],   # SeaBag
        [0.0, 0.4, 2.0, 4.3, 7.7],    # SeaCush
        [0.0, 0.0, 0.0, 1.7, 7.7]     # 技术授权
    ])
    
    bottom = np.zeros(len(years))
    for i, product_data in enumerate(data):
        plt.bar(years, product_data, bottom=bottom, width=PARAMS['bar_width'], 
               label=products[i], color=PARAMS['colors'][i], alpha=PARAMS['bar_alpha'])
        bottom += product_data
    
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('收入 (百万美元)/Revenue (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('产品线收入构成预测/Product Revenue Breakdown', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 使用FontProperties对象设置图例样式
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 增加总收入标签字体大小
    for i, year in enumerate(years):
        plt.text(year, bottom[i] + 1, f'${bottom[i]:.1f}M', 
                ha='center', va='bottom', 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    
    plt.tight_layout()
    plt.show()

# 4. 累计现金流与投资回报分析图
def plot_cash_flow():
    plt.figure(figsize=(11, 7))
    
    yearly_cash_flow = [-1.7, -1.4, 0.8, 8.5, 24.0]
    cumulative_cash_flow = [-1.7, -3.1, -2.3, 6.2, 30.2]
    
    # 增加条形图宽度和线条粗细
    bars = plt.bar(years, yearly_cash_flow, color=PARAMS['colors'][0], alpha=0.7, 
                   width=0.5, label='年度自由现金流/Annual Free Cash Flow')
    
    plt.plot(years, cumulative_cash_flow, 'o-', color=PARAMS['colors'][3], 
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
             label='累计自由现金流/Cumulative Free Cash Flow')
    
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
    
    # 调整投资回报期线条和文字大小
    payback_year = 2028.5
    plt.axvline(x=payback_year, color='green', linestyle='--', alpha=0.7, linewidth=3)
    plt.annotate('Payback Period: 3.5 Years', xy=(payback_year, 0), xytext=(payback_year, -10),
                arrowprops=dict(facecolor='green', shrink=0.05, width=2),
                ha='center', va='top', 
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 增加融资标注字体大小和箭头粗细
    plt.annotate('Series A: $5M', xy=(2025, -1.7), xytext=(2025, -15),
                arrowprops=dict(facecolor='blue', shrink=0.05, width=2),
                ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    plt.annotate('Series B: $10M', xy=(2026.5, -3.1), xytext=(2026.5, -20),
                arrowprops=dict(facecolor='blue', shrink=0.05, width=2),
                ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('现金流 (百万美元)/Cash Flow (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('现金流与投资回报分析/Cash Flow & ROI Analysis', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 使用FontProperties对象设置图例样式
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    plt.ylim(-25, 35)
    plt.xticks(years, [str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    
    plt.tight_layout()
    plt.show()

# 5. 创建用于合并的所有图表函数
def plot_all_charts():
    plt.figure(figsize=(18, 14))
    
    # 调整子图间距
    plt.subplots_adjust(hspace=0.35, wspace=0.35)
    
    # 创建2x2子图布局
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4)
    
    # 1. 主要财务指标增长趋势
    revenue = [1.5, 5.8, 18.4, 42.7, 76.5]
    gross_profit = [0.6, 2.6, 9.2, 23.5, 45.9]
    net_profit = [-0.5, 0.1, 2.4, 10.7, 26.8]
    
    # 增加线条粗细和标记大小
    ax1.plot(years, revenue, 'o-', color=PARAMS['colors'][0], 
            linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
            label='收入/Revenue')
    ax1.plot(years, gross_profit, 's-', color=PARAMS['colors'][2], 
            linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
            label='毛利/Gross Profit')
    ax1.plot(years, net_profit, '^-', color=PARAMS['colors'][3], 
            linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
            label='净利润/Net Profit')
    
    ax1.axvline(x=2026, color='purple', linestyle='--', linewidth=3, alpha=0.7)
    ax1.annotate('Break-even', xy=(2026, 25), xytext=(2026.2, 30),
                arrowprops=dict(facecolor='purple', shrink=0.05, width=2),
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    ax1.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.set_ylabel('金额 (百万美元)/Amount (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.set_title('主要财务指标增长趋势/Financial Growth Indicators', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    
    # 使用FontProperties对象设置图例样式
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend1 = ax1.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend1.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    ax1.set_ylim(-2, 80)
    ax1.set_xticks(years)
    ax1.set_xticklabels([str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.tick_params(axis='y', labelsize=PARAMS['tick_fontsize'], labelcolor='black', width=2)
    
    # 2. 毛利率和净利润率变化
    gross_margin = [40, 45, 50, 55, 60]
    net_margin = [-30, 2, 13, 25, 35]
    
    bar_width = 0.35
    index = np.arange(len(years))
    
    bars1 = ax2.bar(index, gross_margin, bar_width, color=PARAMS['colors'][2], 
                   alpha=PARAMS['bar_alpha'], label='毛利率/Gross Margin')
    bars2 = ax2.bar(index + bar_width, net_margin, bar_width, color=PARAMS['colors'][3], 
                   alpha=PARAMS['bar_alpha'], label='净利润率/Net Margin')
    
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}%', ha='center', va='bottom', 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
                
    for bar in bars2:
        height = bar.get_height()
        if height < 0:
            ypos = height - 2
            va = 'top'
        else:
            ypos = height + 1
            va = 'bottom'
        ax2.text(bar.get_x() + bar.get_width()/2., ypos,
                f'{height}%', ha='center', va=va, 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    
    ax2.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_ylabel('百分比/Percentage (%)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_title('毛利率与净利润率预测/Margin Projections', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(years, fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.tick_params(axis='y', labelsize=PARAMS['tick_fontsize'], labelcolor='black', width=2)
    
    # 使用FontProperties对象设置图例样式
    legend2 = ax2.legend(prop=legend_font)
    legend2.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    ax2.set_ylim(-35, 65)
    ax2.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'], axis='y')
    
    # 3. 产品线收入构成演变
    products = ['SeaFilm', 'SeaBox', 'SeaBag', 'SeaCush', '技术授权/Tech License']
    data = np.array([
        [0.8, 2.8, 7.4, 15.4, 23.7],
        [0.5, 1.7, 5.5, 12.8, 22.1],
        [0.2, 0.9, 3.5, 8.5, 15.3],
        [0.0, 0.4, 2.0, 4.3, 7.7],
        [0.0, 0.0, 0.0, 1.7, 7.7]
    ])
    
    bottom = np.zeros(len(years))
    for i, product_data in enumerate(data):
        ax3.bar(years, product_data, bottom=bottom, width=PARAMS['bar_width'], 
               label=products[i], color=PARAMS['colors'][i], alpha=PARAMS['bar_alpha'])
        bottom += product_data
    
    ax3.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax3.set_ylabel('收入 (百万美元)/Revenue (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax3.set_title('产品线收入构成预测/Product Revenue Breakdown', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 使用FontProperties对象设置图例样式
    legend3 = ax3.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend3.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    ax3.grid(True, linestyle='--', alpha=0.3)
    ax3.tick_params(axis='both', labelsize=PARAMS['tick_fontsize'], width=2)
    
    for i, year in enumerate(years):
        ax3.text(year, bottom[i] + 1, f'${bottom[i]:.1f}M', 
                ha='center', va='bottom', 
                fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    
    # 4. 累计现金流与投资回报分析
    yearly_cash_flow = [-1.7, -1.4, 0.8, 8.5, 24.0]
    cumulative_cash_flow = [-1.7, -3.1, -2.3, 6.2, 30.2]
    
    bars = ax4.bar(years, yearly_cash_flow, color=PARAMS['colors'][0], alpha=0.7, 
                   width=0.5, label='年度自由现金流/Annual Free Cash Flow')
    
    ax4.plot(years, cumulative_cash_flow, 'o-', color=PARAMS['colors'][3], 
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], 
             label='累计自由现金流/Cumulative Free Cash Flow')
    
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
    
    payback_year = 2028.5
    ax4.axvline(x=payback_year, color='green', linestyle='--', alpha=0.7, linewidth=3)
    ax4.annotate('Payback Period: 3.5 Years', xy=(payback_year, 0), xytext=(payback_year, -10),
                arrowprops=dict(facecolor='green', shrink=0.05, width=2),
                ha='center', va='top', 
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    ax4.annotate('Series A: $5M', xy=(2025, -1.7), xytext=(2025, -15),
                arrowprops=dict(facecolor='blue', shrink=0.05, width=2),
                ha='center', 
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    ax4.annotate('Series B: $10M', xy=(2026.5, -3.1), xytext=(2026.5, -20),
                arrowprops=dict(facecolor='blue', shrink=0.05, width=2),
                ha='center', 
                fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'])
    
    ax4.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax4.set_ylabel('现金流 (百万美元)/Cash Flow (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax4.set_title('现金流与投资回报分析/Cash Flow & ROI Analysis', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    
    # 使用FontProperties对象设置图例样式
    legend4 = ax4.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend4.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    
    ax4.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    ax4.set_ylim(-25, 35)
    ax4.tick_params(axis='both', labelsize=PARAMS['tick_fontsize'], width=2)
    
    # 设置总标题并增大字体
    plt.suptitle('海绿科技五年财务预测 (2025-2029) | SeaGreen Tech Five-Year Financial Forecast', 
                 fontsize=PARAMS['suptitle_fontsize'], fontweight=PARAMS['fontweight'], y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()

# 运行函数示例
# 单独展示每个图表
print("展示图表1: 主要财务指标增长趋势")
plot_financial_indicators()

print("展示图表2: 毛利率与净利润率预测")
plot_margin_trends()

print("展示图表3: 产品线收入构成预测")
plot_product_revenue()

print("展示图表4: 现金流与投资回报分析")
plot_cash_flow()

print("展示合并图表")
plot_all_charts()