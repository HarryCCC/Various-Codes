import numpy as np
from scipy.stats import norm

# Hard-coded input parameters 硬编码输入参数

# The weight of each asset 每种资产的权重
weights = np.array([
0.1064,
0.0786,
0.131,
0.0862,
0.0145,
0.0558,
0.0939,
0.0505,
0.03,
0.0352,
0.1171,
0.0487,
0.0241,
0.0561,
0.072,





    0.00   # US$ per A$1 (AU$/US$)
])

# The average return on each asset 每种资产的均值回报率
raw_mean_returns = np.array([
0.0206043958361059,	
0.0206043958361059,	
0.0206043958361059,	
0.0229479345610986,	
0.0124898185173038,	
0.0194265469082734,	
0.0170585250018113,	
0.0122722344290393,	
0.00741707177773288,	
0.0146738461686593,	
0.021778180864641,	
0.00912435777166594,	
0.00863744599771343,	
0.00912435777166602,	
0.00741707177773286,	

    -0.002740  # US$ per A$1 (AU$/US$)
])

# covariance matrix 协方差矩阵
cov_matrix = np.array([
    [0.00785218, 0.00369831, 0.00424846, 0.00439983, 0.00381151, 0.00510416, -0.00009768, 0.00122809, -0.00107017, -0.00056915, 0.00222603, 0.00004924, 0.00018005, 0.00000507, 0.00003397, 0.00158757],
    [0.00369831, 0.00592422, 0.00431986, 0.00410504, 0.00361250, 0.00269653, -0.00006099, 0.00083104, 0.00029068, 0.00122997, 0.00181136, 0.00010755, 0.00020189, 0.00022576, 0.00009805, -0.00095618],
    [0.00424846, 0.00431986, 0.00656636, 0.00548995, 0.00426379, 0.00341114, -0.00006819, 0.00059298, -0.00184803, -0.00088984, 0.00281463, -0.00019998, 0.00006123, 0.00026225, 0.00007023, 0.00180574],
    [0.00439983, 0.00410504, 0.00548995, 0.00985889, 0.00332779, 0.00255974, -0.00024163, 0.00021561, -0.00142118, 0.00028155, 0.00230661, -0.00022415, -0.00016139, 0.00003065, 0.00009894, 0.00100073],
    [0.00381151, 0.00361250, 0.00426379, 0.00332779, 0.00597642, 0.00699646, 0.00010105, 0.00183391, -0.00108530, 0.00061776, 0.00232090, 0.00009436, 0.00043773, 0.00028300, -0.00005713, 0.00059728],
    [0.00510416, 0.00269653, 0.00341114, 0.00255974, 0.00699646, 0.00752565, -0.00007495, 0.00136600, -0.00125239, -0.00065369, 0.00217729, 0.00028081, 0.00075097, 0.00030828, 0.00004505, 0.00132625],
    [-0.00009768, -0.00006099, -0.00006819, -0.00024163, 0.00010105, -0.00007495, 0.00111022, 0.00033327, -0.00008330, 0.00006988, -0.00002236, -0.00004781, -0.00013678, -0.00006541, 0.00007260, 0.00001638],
    [0.00122809, 0.00083104, 0.00059298, 0.00021561, 0.00183391, 0.00136600, 0.00033327, 0.01221837, 0.00075719, 0.00034549, 0.00108455, -0.00055695, -0.00002908, -0.00052284, 0.00017328, -0.00024959],
    [-0.00107017, 0.00029068, -0.00184803, -0.00142118, -0.00108530, -0.00125239, -0.00008330, 0.00075719, 0.00610712, 0.00107101, -0.00111484, 0.00030575, 0.00059427, 0.00025295, -0.00002892, -0.00187992],
    [-0.00056915, 0.00122997, -0.00088984, 0.00028155, 0.00061776, -0.00065369, 0.00006988, 0.00034549, 0.00107101, 0.00226053, -0.00059907, 0.00023036, 0.00003388, -0.00003536, 0.00000987, -0.00249318],
    [0.00222603, 0.00181136, 0.00281463, 0.00230661, 0.00232090, 0.00217729, -0.00002236, 0.00108455, -0.00111484, -0.00059907, 0.00262628, -0.00032621, -0.00003110, -0.00022385, -0.00017720, 0.00115457],
    [0.00004924, 0.00010755, -0.00019998, -0.00022415, 0.00009436, 0.00028081, -0.00004781, -0.00055695, 0.00030575, 0.00023036, -0.00032621, 0.00061615, 0.00044103, 0.00040937, 0.00011283, -0.00024201],
    [0.00018005, 0.00020189, 0.00006123, -0.00016139, 0.00043773, 0.00075097, -0.00013678, -0.00002908, 0.00059427, 0.00003388, -0.00003110, 0.00044103, 0.00085333, 0.00040846, 0.00004665, -0.00015721],
    [0.00000507, 0.00022576, 0.00026225, 0.00003065, 0.00028300, 0.00030828, -0.00006541, -0.00052284, 0.00025295, -0.00003536, -0.00022385, 0.00040937, 0.00040846, 0.00055114, 0.00013785, -0.00000105],
    [0.00003397, 0.00009805, 0.00007023, 0.00009894, -0.00005713, 0.00004505, 0.00007260, 0.00017328, -0.00002892, 0.00000987, -0.00017720, 0.00011283, 0.00004665, 0.00013785, 0.00013221, -0.00004046],
    [0.00158757, -0.00095618, 0.00180574, 0.00100073, 0.00059728, 0.00132625, 0.00001638, -0.00024959, -0.00187992, -0.00249318, 0.00115457, -0.00024201, -0.00015721, -0.00000105, -0.00004046, 0.00312250]
])


# Management fees for each asset (annual)
management_fees_3year = np.array([
    0.0016,  # Australian Equities (AE)
    0.0018,  # World Equities, Unhedged (WE,U)
    0.0018,  # World Equities, Hedged (WE,H)
    0.0050,  # Emerging Markets (EM)

    0.0030,  # World Listed Property (WLP)
    0.0030,  # Australian Listed Property (ALP)
    0.0180,  # Australian Direct Property (ADP)
    0.0025,  # Commodities (CCFs) (COM)
    0.0025,  # Gold (CCFs) (GD)
    0.0250,  # Hedge Funds (HF)
    0.0250,  # US Private Equity (PE)

    0.0025,  # Australian Fixed Income (AFI)
    0.0025,  # Australian Index-Linked Bonds (ILB)
    0.0025,  # World Fixed Income (Hedged) (WFI)
    0.0015,  # Australian Cash (AC)
    0.0000   # US$ per A$1 (AU$/US$)
])
# Convert annual fees to quarterly
fees = (1 + management_fees_3year)**(1/12) - 1
mean_returns = raw_mean_returns - fees


risk_free_rate = 0.0075  # (quarterly) 无风险利率（季度）
time_horizon = 12  # (quarterly) 投资期限(季度)
def calculate_target_quarterly_return(annual_cash_outflow_rate, annual_real_return_rate):
    # Convert annual rates to quarterly rates 将年度利率转换为季度利率
    quarterly_cash_outflow_rate = (1 + annual_cash_outflow_rate) ** (1/4) - 1
    quarterly_real_return_rate = (1 + annual_real_return_rate) ** (1/4) - 1

    # Calculate target quarterly returns 计算目标季度回报率
    target_quarterly_return = (1 + quarterly_cash_outflow_rate) * (1 + quarterly_real_return_rate) - 1

    return target_quarterly_return
# Given condition 给定条件
annual_cash_outflow_rate = 0.05
annual_real_return_rate = 0.03 # not adjusted by inflation 3%+3%
# Calculate target quarterly returns 计算目标季度回报率
target_return = calculate_target_quarterly_return(annual_cash_outflow_rate, annual_real_return_rate)
# target_return = 0.019780  # (quarterly) 目标回报率（季度）

# Calculate the expected return and standard deviation of the portfolio (quarterly) 计算投资组合的期望回报率和标准差 （季度）
portfolio_return = np.sum(weights * mean_returns)
portfolio_stdev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


# 计算三年目标回报率
def calculate_target_triennial_return(annual_cash_outflow_rate, annual_real_return_rate):
    triennial_cash_outflow_rate = (1 + annual_cash_outflow_rate) ** (1/4*12) - 1
    triennial_real_return_rate = (1 + annual_real_return_rate) ** (1/4*12) - 1
    target_triennial_return = (1 + triennial_cash_outflow_rate) * (1 + triennial_real_return_rate) - 1
    return target_triennial_return

target_return_triennial = calculate_target_triennial_return(annual_cash_outflow_rate, annual_real_return_rate)

# 1. 计算三年复合回报率
compound_return_triennial = (1 + portfolio_return)**12 - 1  # 12 quarters in 3 years

# 2. 计算三年夏普比率
sharpe_ratio_triennial = (compound_return_triennial - (1 + risk_free_rate)**12 + 1) / (portfolio_stdev * np.sqrt(12))

# 3. 计算三年索提诺比率
risk_free_rate_triennial = (1 + risk_free_rate)**12 - 1 # 计算三年无风险回报率
def downside_risk(weights, mean_returns, target, cov_matrix):
    # 计算每个资产的下行偏差
    downside_deviation = mean_returns - target
    downside_deviation[downside_deviation > 0] = 0  # 只保留负的偏差
    # 使用下行偏差和协方差矩阵计算整个投资组合的下行风险
    weighted_downside_var = np.dot(weights, np.dot(cov_matrix * np.outer(downside_deviation, downside_deviation), weights.T))
    return np.sqrt(weighted_downside_var)
def semi_deviation_triennial(weights, mean_returns, target, cov_matrix):
    return downside_risk(weights, mean_returns, target, cov_matrix) * np.sqrt(12)
def sortino_ratio_triennial(weights, mean_returns, target_triennial, risk_free_rate_triennial, cov_matrix):
    # 计算投资组合三年的总回报
    portfolio_return_triennial = np.dot(weights, mean_returns) * 12  # 12季度总回报
    # 计算超额回报
    excess_return_triennial = portfolio_return_triennial - risk_free_rate_triennial
    # 计算三年下行风险
    downside_risk_triennial = semi_deviation_triennial(weights, mean_returns, target_triennial, cov_matrix)
    
    if downside_risk_triennial == 0:  # 避免除以零
        return float('inf')
    return excess_return_triennial / downside_risk_triennial

sortino_triennial = sortino_ratio_triennial(weights, mean_returns, target_return_triennial, risk_free_rate_triennial, cov_matrix)

# 4. 三年标准差计算
portfolio_stdev_triennial = portfolio_stdev * np.sqrt(12)

# 5. 三年半标准差计算
semi_dev_triennial = semi_deviation_triennial(weights, mean_returns, target_return_triennial, cov_matrix)

# 6. 计算三年期间损失概率
prob_loss_triennial = norm.cdf(-compound_return_triennial / (portfolio_stdev * np.sqrt(12)))

# 7. 计算三年条件在险价值(CVaR)或期望亏空
conf_level = 0.95   # Assumed confidence 假设置信度
cvar_triennial = norm.ppf(1 - conf_level, compound_return_triennial, portfolio_stdev * np.sqrt(12))
cvar_triennial = (compound_return_triennial - cvar_triennial) / (1 - conf_level) - compound_return_triennial

# 8. 计算三年未达目标回报率概率
prob_under_target_triennial = norm.cdf((target_return_triennial - compound_return_triennial) / (portfolio_stdev * np.sqrt(12)))

# 打印所有三年期计算结果
print(" ")
print(f"Triennial Compound Return: {compound_return_triennial:.4f}")
print(f"Triennial Sharpe Ratio: {sharpe_ratio_triennial:.4f}")
print(f"Triennial Sortino Ratio: {sortino_triennial:.4f}")
print(f"Portfolio Standard Deviation over 3 Years: {portfolio_stdev_triennial:.4f}")
print(f"Portfolio Semi-Deviation over 3 Years: {semi_dev_triennial:.4f}")
print(f"Conditional Value at Risk (CVaR), Triennial: {cvar_triennial:.4f}{'%'}")
print(f"Probability of Not Meeting Triennial Return Target: {100*prob_under_target_triennial:.4f}{'%'}")
print(f"Probability of Loss over 3 Years: {100*prob_loss_triennial:.4f}{'%'}")