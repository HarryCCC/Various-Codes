import numpy as np
from scipy.stats import norm

# Hard-coded input parameters 硬编码输入参数

# The weight of each asset 每种资产的权重
weights = np.array([
    0.27,  # Australian Equities (AE)
    0.10,  # World Equities, Unhedged (WE,U)
    0.09,  # World Equities, Hedged (WE,H)
    0.03,  # Emerging Markets (EM)

    0.00,  # World Listed Property (WLP)
    0.05,  # Australian Listed Property (ALP)
    0.05,  # Australian Direct Property (ADP)
    0.00,  # Commodities (CCFs) (COM)
    0.00,  # Gold (CCFs) (GD)
    0.05,  # Hedge Funds (HF)
    0.15,  # US Private Equity (PE)

    0.09,  # Australian Fixed Income (AFI)
    0.03,  # Australian Index-Linked Bonds (ILB)
    0.02,  # World Fixed Income (Hedged) (WFI)
    0.07,  # Australian Cash (AC)
    0.00   # US$ per A$1 (AU$/US$)
])

# The average return on each asset 每种资产的均值回报率
raw_mean_returns = np.array([
    0.025837,  # Australian Equities (AE)
    0.025088,  # World Equities, Unhedged (WE,U)
    0.026602,  # World Equities, Hedged (WE,H)
    0.022344,  # Emerging Markets (EM)

    0.012490,  # World Listed Property (WLP)
    0.023816,  # Australian Listed Property (ALP)
    0.022882,  # Australian Direct Property (ADP)
    0.011773,  # Commodities (CCFs) (COM)
    0.009653,  # Gold (CCFs) (GD)
    0.019426,  # Hedge Funds (HF)
    0.018764,  # US Private Equity (PE)

    0.018728,  # Australian Fixed Income (AFI)
    0.015875,  # Australian Index-Linked Bonds (ILB)
    0.020283,  # World Fixed Income (Hedged) (WFI)
    0.016815,  # Australian Cash (AC)
    -0.002740  # US$ per A$1 (AU$/US$)
])

# Standard deviation per asset (useless) 每种资产标准差（无用）
stdevs = np.array([
    0.088613,  # Australian Equities (AE)
    0.076969,  # World Equities, Unhedged (WE,U)
    0.081033,  # World Equities, Hedged (WE,H)
    0.099292,  # Emerging Markets (EM)

    0.077307,  # World Listed Property (WLP)
    0.086750,  # Australian Listed Property (ALP)
    0.033320,  # Australian Direct Property (ADP)
    0.110537,  # Commodities (CCFs) (COM)
    0.078148,  # Gold (CCFs) (GD)
    0.047545,  # Hedge Funds (HF)
    0.051247,  # US Private Equity (PE)

    0.024822,  # Australian Fixed Income (AFI)
    0.029212,  # Australian Index-Linked Bonds (ILB)
    0.023476,  # World Fixed Income (Hedged) (WFI)
    0.011498,  # Australian Cash (AC)
    0.055879   # US$ per A$1 (AU$/US$)
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
management_fees_annual = np.array([
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
fees = (1 + management_fees_annual)**(1/4) - 1
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
annual_real_return_rate = 0.03 + 0.03 # adjusted by inflation
# Calculate target quarterly returns 计算目标季度回报率
target_return = calculate_target_quarterly_return(annual_cash_outflow_rate, annual_real_return_rate)
# target_return = 0.019780  # (quarterly) 目标回报率（季度）


# Calculate the expected return and standard deviation of the portfolio (quarterly) 计算投资组合的期望回报率和标准差 （季度）
portfolio_return = np.sum(weights * mean_returns)
portfolio_stdev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


# Calculate the parameters of the portfolio 计算投资组合的各项参数
# 1. Compound annual return 复合年化回报率（年度）
compound_return = ((1 + portfolio_return)**time_horizon)**(4/time_horizon) - 1

# 2. Sharpe ratio (quarterly) 夏普比率（季度）
sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_stdev

# 3. Sotino ratio (quarterly) 索提诺比率（季度）
def downside_risk(weights, mean_returns, target, cov_matrix):
    # 计算每个资产的下行偏差
    downside_deviation = mean_returns - target
    downside_deviation[downside_deviation > 0] = 0  # 只保留负的偏差
    # 使用下行偏差和协方差矩阵计算整个投资组合的下行风险
    weighted_downside_var = np.dot(weights, np.dot(cov_matrix * np.outer(downside_deviation, downside_deviation), weights.T))
    return np.sqrt(weighted_downside_var)

def sortino_ratio(weights, mean_returns, target, risk_free_rate, cov_matrix):
    portfolio_return = np.dot(weights, mean_returns)
    excess_return = portfolio_return - risk_free_rate
    downside_risk_value = downside_risk(weights, mean_returns, target, cov_matrix)
    
    if downside_risk_value == 0:  # 避免除以零
        return float('inf')
    return excess_return / downside_risk_value

sortino = sortino_ratio(weights, mean_returns, target_return, risk_free_rate, cov_matrix)

# 4. Annualized standard deviation of portfolio value (%) (annual) 投资组合价值的年化标准差(%)（年度）
portfolio_stdev_pa = portfolio_stdev * np.sqrt(4) * 100  # 一年4个季度

# 5. Annualized half standard deviation (quarterly) 半标准差（季度）
def semi_deviation(weights, mean_returns, target, cov_matrix):
    return downside_risk(weights, mean_returns, target, cov_matrix)

semi_dev = semi_deviation(weights, mean_returns, target_return, cov_matrix)*100

# 6. Annualized tracking error relative to the baseline (%) (annual) 相对基准的年化跟踪误差(%) （年度）
benchmark_return = 0.0206   # Benchmark return (quarterly) 基准回报率（季度）
tracking_error = np.sqrt(np.sum((mean_returns - benchmark_return)**2 * weights)) * np.sqrt(4) * 100

# 7. Probability of loss over a 3-year period 3年期间损失概率
prob_loss = norm.cdf( -portfolio_return * time_horizon / (portfolio_stdev * np.sqrt(time_horizon)))

# 8. Conditional value at Risk (CVaR) or expected deficit (quarterly) 条件在险价值(CVaR)或期望亏空（季度）
conf_level = 0.95   # Assumed confidence 假设置信度
var_95 = norm.ppf(1-conf_level, portfolio_return, portfolio_stdev)
cvar_95 = (portfolio_return - var_95) / (1 - conf_level) - portfolio_return

# 9. Probability of missing target Return (quarterly) 未达目标回报率概率（季度）
prob_under_target = norm.cdf((target_return - portfolio_return) / portfolio_stdev)


# Print result 打印结果
print(f"Compound Return (p.a.): {compound_return:.4f}")
print(f"Sharpe Ratio: {sharpe_ratio:.4f}") 
print(f"Sortino Ratio: {sortino:.4f}")
print(f"Std Dev (Portfolio Value), % pa: {portfolio_stdev_pa:.4f}") 
print(f"Semi-Deviation, % pa: {semi_dev:.4f}")
print(f"Tracking Error vs Benchmark, % pa: {tracking_error:.4f}")
print(f"Probability of Loss over {time_horizon} Quarters: {prob_loss:.4f}")
print(f"Conditional Value at Risk (CVaR) or Expected Shortfall at 95% confidence, % pa: {cvar_95:.4f}")
print(f"Probability of Not Meeting Return Target: {prob_under_target:.4f}")