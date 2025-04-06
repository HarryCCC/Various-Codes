# Import necessary libraries
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# Parameter library - Centralized management of chart visual element settings
PARAMS = {
    # Font size settings
    'title_fontsize': 24,       # Main title font size
    'subtitle_fontsize': 20,    # Subplot title font size
    'suptitle_fontsize': 26,    # Super title font size
    'axis_label_fontsize': 18,  # Axis label font size
    'tick_fontsize': 16,        # Tick label font size
    'legend_fontsize': 18,      # Legend font size (Adjusted slightly for better fit)
    'annotation_fontsize': 16,  # Annotation text font size
    'data_label_fontsize': 16,  # Data label font size

    # Line and marker settings
    'linewidth': 4,             # Line width
    'markersize': 10,           # Marker size
    'grid_alpha': 0.6,          # Grid transparency (Slightly adjusted)
    'bar_width': 0.7,           # Bar chart width
    'bar_alpha': 0.8,           # Bar chart transparency

    # Legend settings
    'legend_linewidth': 2,      # Legend border line width
    'legend_loc': 'upper left', # Legend location

    # Font style
    'fontweight': 'bold',       # Font weight

    # Color settings
    'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'], # Main colors
}

# Set Chinese font, choose one available on the system
# Prioritize fonts commonly available on various systems
try:
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
except:
    print("Warning: Suitable Chinese font not found, using default sans-serif.")
plt.rcParams['axes.unicode_minus'] = False  # Resolve negative sign display issue
plt.rcParams['legend.handlelength'] = 3   # Increase line length in legend
plt.rcParams['legend.handleheight'] = 1.5  # Increase line height in legend
plt.rcParams['legend.handletextpad'] = 0.8 # Increase spacing between marker and text in legend
plt.rcParams['legend.borderpad'] = 1.0    # Increase padding inside legend
plt.rcParams['legend.frameon'] = True     # Show legend border
plt.rcParams['legend.edgecolor'] = '0.8'  # Set legend border color

# Define common year data
years = np.array([2025, 2026, 2027, 2028, 2029])

# 1. Financial Growth Indicators Chart (Updated Data)
def plot_financial_indicators_revised():
    """Plots the trend of key financial indicators with revised data."""
    plt.figure(figsize=(11, 7))

    # --- Updated Data ---
    revenue = [1.0, 2.5, 5.5, 9.5, 15.5]
    gross_profit = [0.3, 0.8, 2.0, 3.8, 7.4]
    net_profit = [-0.8, -0.9, 0.1, 0.9, 2.4]
    # --------------------

    # Plotting lines with updated styles
    plt.plot(years, revenue, 'o-', color=PARAMS['colors'][0],
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'],
             label='收入/Revenue')
    plt.plot(years, gross_profit, 's-', color=PARAMS['colors'][2],
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'],
             label='毛利/Gross Profit')
    plt.plot(years, net_profit, '^-', color=PARAMS['colors'][3],
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'],
             label='净利润/Net Profit')

    # Mark break-even point (Updated to 2027)
    break_even_year = 2027
    plt.axvline(x=break_even_year, color='purple', linestyle='--', linewidth=3, alpha=0.7)
    # Adjust annotation position based on new data range
    plt.annotate('Break-even (Year)', xy=(break_even_year, 0.1), xytext=(break_even_year + 0.2, 5), # Adjusted position
                 arrowprops=dict(facecolor='purple', shrink=0.05, width=2, headwidth=8),
                 fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='purple')

    # Labels and Title
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('金额 (百万美元)/Amount (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('主要财务指标增长趋势/Financial Growth Indicators', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])

    # Legend styling
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])

    # Adjust Y-axis limits based on new data
    plt.ylim(-2, 18) # Adjusted limit

    # Tick styling
    plt.xticks(years, [str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])

    plt.tight_layout()
    plt.show()

# 2. Margin Trends Chart (Updated Data)
def plot_margin_trends_revised():
    """Plots the trend of gross and net margins with revised data."""
    plt.figure(figsize=(11, 7))

    # --- Updated Data ---
    gross_margin = [28, 32, 36, 40, 48]
    net_margin = [-80, -36, 2, 9, 15]
    # --------------------

    bar_width = 0.35
    index = np.arange(len(years))

    # Plotting bars
    bars1 = plt.bar(index, gross_margin, bar_width, color=PARAMS['colors'][2],
                    alpha=PARAMS['bar_alpha'], label='毛利率/Gross Margin')
    bars2 = plt.bar(index + bar_width, net_margin, bar_width, color=PARAMS['colors'][3],
                    alpha=PARAMS['bar_alpha'], label='净利润率/Net Margin')

    # Adding data labels
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                 f'{height}%', ha='center', va='bottom',
                 fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])

    for bar in bars2:
        height = bar.get_height()
        if height < 0:
            ypos = height - 3 # Adjusted offset for negative values
            va = 'top'
        else:
            ypos = height + 1
            va = 'bottom'
        plt.text(bar.get_x() + bar.get_width()/2., ypos,
                 f'{height}%', ha='center', va=va,
                 fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])

    # Labels and Title
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('百分比/Percentage (%)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('毛利率与净利润率预测/Margin Projections', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])
    plt.xticks(index + bar_width / 2, years, fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])

    # Legend styling
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])

    # Adjust Y-axis limits based on new data
    plt.ylim(-90, 60) # Adjusted limit
    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'], axis='y')

    plt.tight_layout()
    plt.show()

# 3. Product Revenue Breakdown Chart (Illustrative Updated Data)
def plot_product_revenue_revised():
    """Plots the product revenue breakdown with illustrative revised data."""
    plt.figure(figsize=(11, 7))

    products = ['SeaFilm', 'SeaBox', 'SeaBag', 'SeaCush', '技术授权/Tech License']
    # --- Illustrative Updated Data (sums to revised total revenue) ---
    # Note: This breakdown is illustrative as the revised report didn't provide specifics.
    data = np.array([
        [0.5, 1.1, 2.0, 3.0, 4.0],  # SeaFilm
        [0.3, 0.7, 1.5, 2.5, 4.0],  # SeaBox
        [0.1, 0.4, 1.0, 2.0, 3.5],  # SeaBag
        [0.1, 0.3, 0.5, 1.0, 2.0],  # SeaCush
        [0.0, 0.0, 0.5, 1.0, 2.0]   # Tech License
    ])
    # Total Revenue Check: data.sum(axis=0) -> [ 1.   2.5  5.5  9.5 15.5] - Matches revised totals
    # --------------------------------------------------------------------

    bottom = np.zeros(len(years))
    for i, product_data in enumerate(data):
        plt.bar(years, product_data, bottom=bottom, width=PARAMS['bar_width'],
                label=products[i], color=PARAMS['colors'][i % len(PARAMS['colors'])], alpha=PARAMS['bar_alpha']) # Use modulo for color cycling
        bottom += product_data

    # Labels and Title
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('收入 (百万美元)/Revenue (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('产品线收入构成预测 (示例)/Product Revenue Breakdown (Illustrative)', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight']) # Added Illustrative note

    # Legend styling
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])

    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(years, [str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight']) # Ensure years are shown
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])

    # Adding total revenue labels
    for i, year in enumerate(years):
        plt.text(year, bottom[i] + 0.5, f'${bottom[i]:.1f}M', # Adjusted vertical offset
                 ha='center', va='bottom',
                 fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])

    # Adjust Y-axis limits based on new data
    plt.ylim(0, 18) # Adjusted limit

    plt.tight_layout()
    plt.show()

# 4. Cash Flow & Funding Analysis Chart (Updated Data)
def plot_cash_flow_revised():
    """Plots cash flow analysis with revised data and funding rounds."""
    plt.figure(figsize=(11, 7))

    # --- Updated Data ---
    yearly_cash_flow = [-1.6, -2.0, -1.8, -1.5, 0.8]
    cumulative_cash_flow = [-1.6, -3.6, -5.4, -6.9, -6.1]
    # --------------------

    # Plotting bars and lines
    bars = plt.bar(years, yearly_cash_flow, color=PARAMS['colors'][0], alpha=0.7,
                   width=0.5, label='年度自由现金流/Annual Free Cash Flow')

    plt.plot(years, cumulative_cash_flow, 'o-', color=PARAMS['colors'][3],
             linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'],
             label='累计自由现金流/Cumulative Free Cash Flow')

    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)

    # --- Removed Payback Period Annotation as cumulative FCF remains negative ---

    # Funding round annotations (adjust positions if needed)
    plt.annotate('Series A: $5M', xy=(2025, -1.6), xytext=(2025, -8), # Adjusted position
                 arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8),
                 ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='blue')

    # Assuming Series B happens around Q3 2026 as per original plan
    series_b_year_approx = 2026.75
    # Find corresponding cumulative cash flow around that time (interpolate or use 2026/2027 values)
    # Let's point near the 2027 cumulative value for placement
    plt.annotate('Series B: $10M', xy=(series_b_year_approx, -4.5), xytext=(series_b_year_approx, -12), # Adjusted position
                 arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8),
                 ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='blue')

    # Labels and Title
    plt.xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.ylabel('现金流 (百万美元)/Cash Flow (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    plt.title('现金流与融资分析/Cash Flow & Funding Analysis', fontsize=PARAMS['title_fontsize'], fontweight=PARAMS['fontweight'])

    # Legend styling
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])
    legend = plt.legend(loc='lower right', prop=legend_font) # Adjusted location for better fit
    legend.get_frame().set_linewidth(PARAMS['legend_linewidth'])

    plt.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    # Adjust Y-axis limits based on new data
    plt.ylim(-15, 5) # Adjusted limit
    plt.xticks(years, [str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    plt.yticks(fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])

    plt.tight_layout()
    plt.show()

# 5. Combined Chart Function (Updated Data)
def plot_all_charts_revised():
    """Plots all four charts in a 2x2 grid with revised data."""
    plt.figure(figsize=(18, 14))
    plt.subplots_adjust(hspace=0.4, wspace=0.3) # Increased spacing slightly

    # Create 2x2 subplot layout
    ax1 = plt.subplot(2, 2, 1)
    ax2 = plt.subplot(2, 2, 2)
    ax3 = plt.subplot(2, 2, 3)
    ax4 = plt.subplot(2, 2, 4)

    # --- Common Font Property ---
    legend_font = FontProperties(weight=PARAMS['fontweight'], size=PARAMS['legend_fontsize'])

    # --- Chart 1: Financial Indicators (Revised) ---
    revenue = [1.0, 2.5, 5.5, 9.5, 15.5]
    gross_profit = [0.3, 0.8, 2.0, 3.8, 7.4]
    net_profit = [-0.8, -0.9, 0.1, 0.9, 2.4]
    ax1.plot(years, revenue, 'o-', color=PARAMS['colors'][0], linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], label='收入/Revenue')
    ax1.plot(years, gross_profit, 's-', color=PARAMS['colors'][2], linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], label='毛利/Gross Profit')
    ax1.plot(years, net_profit, '^-', color=PARAMS['colors'][3], linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], label='净利润/Net Profit')
    break_even_year = 2027
    ax1.axvline(x=break_even_year, color='purple', linestyle='--', linewidth=3, alpha=0.7)
    ax1.annotate('Break-even (Year)', xy=(break_even_year, 0.1), xytext=(break_even_year + 0.2, 5),
                 arrowprops=dict(facecolor='purple', shrink=0.05, width=2, headwidth=8),
                 fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='purple')
    ax1.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.set_ylabel('金额 (百万美元)/Amount (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.set_title('主要财务指标增长趋势', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    legend1 = ax1.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend1.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    ax1.set_ylim(-2, 18)
    ax1.set_xticks(years)
    ax1.set_xticklabels([str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    ax1.tick_params(axis='y', labelsize=PARAMS['tick_fontsize'])


    # --- Chart 2: Margins (Revised) ---
    gross_margin = [28, 32, 36, 40, 48]
    net_margin = [-80, -36, 2, 9, 15]
    bar_width = 0.35
    index = np.arange(len(years))
    bars1_ax2 = ax2.bar(index, gross_margin, bar_width, color=PARAMS['colors'][2], alpha=PARAMS['bar_alpha'], label='毛利率/Gross Margin')
    bars2_ax2 = ax2.bar(index + bar_width, net_margin, bar_width, color=PARAMS['colors'][3], alpha=PARAMS['bar_alpha'], label='净利润率/Net Margin')
    # Add data labels for ax2
    for bar in bars1_ax2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height}%', ha='center', va='bottom', fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    for bar in bars2_ax2:
        height = bar.get_height()
        ypos = height + 1 if height >= 0 else height - 3
        va = 'bottom' if height >= 0 else 'top'
        ax2.text(bar.get_x() + bar.get_width()/2., ypos, f'{height}%', ha='center', va=va, fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    ax2.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_ylabel('百分比/Percentage (%)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_title('毛利率与净利润率预测', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.set_xticks(index + bar_width / 2)
    ax2.set_xticklabels(years, fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    ax2.tick_params(axis='y', labelsize=PARAMS['tick_fontsize'])
    legend2 = ax2.legend(prop=legend_font)
    legend2.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    ax2.set_ylim(-90, 60)
    ax2.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'], axis='y')


    # --- Chart 3: Product Revenue (Illustrative Revised) ---
    products = ['SeaFilm', 'SeaBox', 'SeaBag', 'SeaCush', '技术授权/Tech License']
    data_ax3 = np.array([ # Illustrative data
        [0.5, 1.1, 2.0, 3.0, 4.0], [0.3, 0.7, 1.5, 2.5, 4.0], [0.1, 0.4, 1.0, 2.0, 3.5],
        [0.1, 0.3, 0.5, 1.0, 2.0], [0.0, 0.0, 0.5, 1.0, 2.0]
    ])
    bottom_ax3 = np.zeros(len(years))
    for i, product_data in enumerate(data_ax3):
        ax3.bar(years, product_data, bottom=bottom_ax3, width=PARAMS['bar_width'], label=products[i], color=PARAMS['colors'][i % len(PARAMS['colors'])], alpha=PARAMS['bar_alpha'])
        bottom_ax3 += product_data
    ax3.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax3.set_ylabel('收入 (百万美元)/Revenue (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax3.set_title('产品线收入构成预测 (示例)', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    legend3 = ax3.legend(loc=PARAMS['legend_loc'], prop=legend_font)
    legend3.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    ax3.grid(True, linestyle='--', alpha=0.3)
    ax3.tick_params(axis='both', labelsize=PARAMS['tick_fontsize'])
    ax3.set_xticks(years) # Ensure years are shown as ticks
    ax3.set_xticklabels([str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    for i, year in enumerate(years):
        ax3.text(year, bottom_ax3[i] + 0.5, f'${bottom_ax3[i]:.1f}M', ha='center', va='bottom', fontweight=PARAMS['fontweight'], fontsize=PARAMS['data_label_fontsize'])
    ax3.set_ylim(0, 18)


    # --- Chart 4: Cash Flow (Revised) ---
    yearly_cash_flow = [-1.6, -2.0, -1.8, -1.5, 0.8]
    cumulative_cash_flow = [-1.6, -3.6, -5.4, -6.9, -6.1]
    ax4.bar(years, yearly_cash_flow, color=PARAMS['colors'][0], alpha=0.7, width=0.5, label='年度自由现金流/Annual Free Cash Flow')
    ax4.plot(years, cumulative_cash_flow, 'o-', color=PARAMS['colors'][3], linewidth=PARAMS['linewidth'], markersize=PARAMS['markersize'], label='累计自由现金流/Cumulative Free Cash Flow')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=2)
    # Funding annotations for ax4
    ax4.annotate('Series A: $5M', xy=(2025, -1.6), xytext=(2025, -8), arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='blue')
    series_b_year_approx = 2026.75
    ax4.annotate('Series B: $10M', xy=(series_b_year_approx, -4.5), xytext=(series_b_year_approx, -12), arrowprops=dict(facecolor='blue', shrink=0.05, width=2, headwidth=8), ha='center', fontsize=PARAMS['annotation_fontsize'], fontweight=PARAMS['fontweight'], color='blue')
    ax4.set_xlabel('年份/Year', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax4.set_ylabel('现金流 (百万美元)/Cash Flow (Million USD)', fontsize=PARAMS['axis_label_fontsize'], fontweight=PARAMS['fontweight'])
    ax4.set_title('现金流与融资分析', fontsize=PARAMS['subtitle_fontsize'], fontweight=PARAMS['fontweight'])
    legend4 = ax4.legend(loc='lower right', prop=legend_font)
    legend4.get_frame().set_linewidth(PARAMS['legend_linewidth'])
    ax4.grid(True, linestyle='--', alpha=PARAMS['grid_alpha'])
    ax4.set_ylim(-15, 5)
    ax4.set_xticks(years)
    ax4.set_xticklabels([str(year) for year in years], fontsize=PARAMS['tick_fontsize'], fontweight=PARAMS['fontweight'])
    ax4.tick_params(axis='y', labelsize=PARAMS['tick_fontsize'])

    # --- Super Title ---
    plt.suptitle('海绿科技五年财务预测 (2025-2029) | SeaGreen Tech Five-Year Financial Forecast',
                 fontsize=PARAMS['suptitle_fontsize'], fontweight=PARAMS['fontweight'], y=0.98)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
    plt.show()


# --- Example Function Calls ---
# Show each chart individually
print("展示图表1: 主要财务指标增长趋势 (修订版数据)")
plot_financial_indicators_revised()

print("展示图表2: 毛利率与净利润率预测 (修订版数据)")
plot_margin_trends_revised()

print("展示图表3: 产品线收入构成预测 (修订版示例数据)")
plot_product_revenue_revised()

print("展示图表4: 现金流与融资分析 (修订版数据)")
plot_cash_flow_revised()

# Show the combined chart
print("展示合并图表 (修订版数据)")
plot_all_charts_revised()
