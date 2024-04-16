import numpy as np
import matplotlib.pyplot as plt
import os

# Hard-coded parameters
asset_classes = np.array(["AE", "WE,U", "WE,H", "EM", "WLP", "ALP", "ADP", "COM", "GD", "HF", "PE", "AFI", "ILB", "WFI", "AC"])
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
])
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
])
fees = (1 + management_fees_annual)**(1/4) - 1
mean_returns = raw_mean_returns - fees
cov_matrix = np.array([
    [0.00785218, 0.00369831, 0.00424846, 0.00439983, 0.00381151, 0.00510416, -0.00009768, 0.00122809, -0.00107017, -0.00056915, 0.00222603, 0.00004924, 0.00018005, 0.00000507, 0.00003397],
    [0.00369831, 0.00592422, 0.00431986, 0.00410504, 0.00361250, 0.00269653, -0.00006099, 0.00083104, 0.00029068, 0.00122997, 0.00181136, 0.00010755, 0.00020189, 0.00022576, 0.00009805],
    [0.00424846, 0.00431986, 0.00656636, 0.00548995, 0.00426379, 0.00341114, -0.00006819, 0.00059298, -0.00184803, -0.00088984, 0.00281463, -0.00019998, 0.00006123, 0.00026225, 0.00007023],
    [0.00439983, 0.00410504, 0.00548995, 0.00985889, 0.00332779, 0.00255974, -0.00024163, 0.00021561, -0.00142118, 0.00028155, 0.00230661, -0.00022415, -0.00016139, 0.00003065, 0.00009894],
    [0.00381151, 0.00361250, 0.00426379, 0.00332779, 0.00597642, 0.00699646, 0.00010105, 0.00183391, -0.00108530, 0.00061776, 0.00232090, 0.00009436, 0.00043773, 0.00028300, -0.00005713],
    [0.00510416, 0.00269653, 0.00341114, 0.00255974, 0.00699646, 0.00752565, -0.00007495, 0.00136600, -0.00125239, -0.00065369, 0.00217729, 0.00028081, 0.00075097, 0.00030828, 0.00004505],
    [-0.00009768, -0.00006099, -0.00006819, -0.00024163, 0.00010105, -0.00007495, 0.00111022, 0.00033327, -0.00008330, 0.00006988, -0.00002236, -0.00004781, -0.00013678, -0.00006541, 0.00007260],
    [0.00122809, 0.00083104, 0.00059298, 0.00021561, 0.00183391, 0.00136600, 0.00033327, 0.01221837, 0.00075719, 0.00034549, 0.00108455, -0.00055695, -0.00002908, -0.00052284, 0.00017328],
    [-0.00107017, 0.00029068, -0.00184803, -0.00142118, -0.00108530, -0.00125239, -0.00008330, 0.00075719, 0.00610712, 0.00107101, -0.00111484, 0.00030575, 0.00059427, 0.00025295, -0.00002892],
    [-0.00056915, 0.00122997, -0.00088984, 0.00028155, 0.00061776, -0.00065369, 0.00006988, 0.00034549, 0.00107101, 0.00226053, -0.00059907, 0.00023036, 0.00003388, -0.00003536, 0.00000987],
    [0.00222603, 0.00181136, 0.00281463, 0.00230661, 0.00232090, 0.00217729, -0.00002236, 0.00108455, -0.00111484, -0.00059907, 0.00262628, -0.00032621, -0.00003110, -0.00022385, -0.00017720],
    [0.00004924, 0.00010755, -0.00019998, -0.00022415, 0.00009436, 0.00028081, -0.00004781, -0.00055695, 0.00030575, 0.00023036, -0.00032621, 0.00061615, 0.00044103, 0.00040937, 0.00011283],
    [0.00018005, 0.00020189, 0.00006123, -0.00016139, 0.00043773, 0.00075097, -0.00013678, -0.00002908, 0.00059427, 0.00003388, -0.00003110, 0.00044103, 0.00085333, 0.00040846, 0.00004665],
    [0.00000507, 0.00022576, 0.00026225, 0.00003065, 0.00028300, 0.00030828, -0.00006541, -0.00052284, 0.00025295, -0.00003536, -0.00022385, 0.00040937, 0.00040846, 0.00055114, 0.00013785],
    [0.00003397, 0.00009805, 0.00007023, 0.00009894, -0.00005713, 0.00004505, 0.00007260, 0.00017328, -0.00002892, 0.00000987, -0.00017720, 0.00011283, 0.00004665, 0.00013785, 0.00013221]
])

risk_free_rate = 0.0075  # Quarterly risk-free rate
num_portfolios = 5000000
min_required_return = (1.08 ** 0.25) - 1  # Minimum required return

# Simulate random portfolios
results = np.zeros((3, num_portfolios))
weights_record = []

# Simulate random portfolios and record progress
for i in range(num_portfolios):
    weights = np.random.random(len(asset_classes))
    weights /= np.sum(weights)
    weights_record.append(weights)

    portfolio_return = np.dot(weights, mean_returns)
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std

    results[0, i] = portfolio_return
    results[1, i] = portfolio_std
    results[2, i] = sharpe_ratio

    # Display progress at the specified interval
    if (i + 1) % (num_portfolios/100) == 0 or i == num_portfolios - 1:
        progress_percent = ((i + 1) / num_portfolios) * 100
        print(f"Progress: {progress_percent:.2f}%")

# Apply minimum return filter
valid_indices = np.where(results[0] >= min_required_return)
filtered_results = results[:, valid_indices[0]]
filtered_weights = [weights_record[i] for i in valid_indices[0]]

# Find the optimal portfolios from filtered results
highest_sharpe_idx = filtered_results[2].argmax()
min_variance_idx = filtered_results[1].argmin()

max_sharpe_return = filtered_results[0, highest_sharpe_idx]
max_sharpe_std = filtered_results[1, highest_sharpe_idx]
max_sharpe_weights = filtered_weights[highest_sharpe_idx]

min_variance_return = filtered_results[0, min_variance_idx]
min_variance_std = filtered_results[1, min_variance_idx]
min_variance_weights = filtered_weights[min_variance_idx]

# Print optimal portfolio information
print("Optimal Sharpe Portfolio")
print("Quarterly Return: {:.2%}".format(max_sharpe_return)) 
print("Quarterly Volatility: {:.2%}".format(max_sharpe_std))
print("Weights:")
for i in range(len(asset_classes)):
    print(" {}: {:.4%}".format(asset_classes[i], max_sharpe_weights[i]))

print("\nMinimum Variance Portfolio") 
print("Quarterly Return: {:.2%}".format(min_variance_return))
print("Quarterly Volatility: {:.2%}".format(min_variance_std))  
print("Weights:")
for i in range(len(asset_classes)):
    print(" {}: {:.4%}".format(asset_classes[i], min_variance_weights[i]))

# Plot the efficient frontier
plt.figure(figsize=(10,8))
plt.scatter(results[1]*100, results[0]*100, c=results[2], cmap='viridis')
plt.colorbar(label='Sharpe Ratio')
plt.xlabel('Quarterly Standard Deviation (%)')
plt.ylabel('Quarterly Expected Return (%)')
plt.scatter(max_sharpe_std*100, max_sharpe_return*100, marker=(5,1,0), color='r', s=100, label='Maximum Sharpe ratio')
plt.scatter(min_variance_std*100, min_variance_return*100, marker=(5,1,0), color='m', s=100, label='Minimum variance')
plt.plot([0, max_sharpe_std*100], [risk_free_rate*100, max_sharpe_return*100], linestyle='--', color='black', label='Capital Allocation Line (CAL)')  
plt.title('Efficient Frontier')
# Draw horizontal line for minimum required return
plt.axhline(y=min_required_return * 100, color='y', linestyle='--', label='Minimum Required Return')
plt.legend(labelspacing=0.8)
# 自适应调整x轴和y轴范围
std_min, std_max = np.min(results[1]*100), np.max(results[1]*100)
ret_min, ret_max = np.min(results[0]*100), np.max(results[0]*100)
# 设置x轴范围为标准差的最小值和最大值,并留出10%的边距
margin_x = (std_max - std_min) * 0.1
plt.xlim(std_min - margin_x, std_max + margin_x)
# 设置y轴范围为收益率的最小值和最大值,并留出10%的边距  
margin_y = (ret_max - ret_min) * 0.1
plt.ylim(ret_min - margin_y, ret_max + margin_y)
plt.grid(True)


# 获取当前脚本所在路径
script_path = os.path.dirname(os.path.abspath(__file__))

def unique_filename(directory, base_name, extension):
    """Generate a unique file name in the given directory."""
    counter = 1
    while True:
        if counter == 1:
            new_name = f"{base_name}.{extension}"
        else:
            new_name = f"{base_name}({counter}).{extension}"
        full_path = os.path.join(directory, new_name)
        if not os.path.exists(full_path):
            return full_path
        counter += 1

# Calculate the desired name part
million_portfolios = (num_portfolios) / 1000000
# Generate unique filenames
weights_file = unique_filename(script_path, f"{million_portfolios:.2f}mil_Random_portfolio_weights", 'txt')
frontier_image = unique_filename(script_path, f"{million_portfolios:.2f}mil_Random_efficient_frontier", 'png')

# Saving portfolio weights to a text file
with open(weights_file, 'w') as file:
    file.write("Optimal Sharpe Portfolio\n")
    file.write(f"Quarterly Return: {max_sharpe_return:.2%}\n")
    file.write(f"Quarterly Volatility: {max_sharpe_std:.2%}\n")
    file.write("Weights:\n")
    for asset, weight in zip(asset_classes, max_sharpe_weights):
        file.write(f"{asset}: {weight:.4%}\n")
    file.write("\nMinimum Variance Portfolio\n")
    file.write(f"Quarterly Return: {min_variance_return:.2%}\n")
    file.write(f"Quarterly Volatility: {min_variance_std:.2%}\n")
    file.write("Weights:\n")
    for asset, weight in zip(asset_classes, min_variance_weights):
        file.write(f"{asset}: {weight:.4%}\n")

plt.savefig(frontier_image)

plt.show()

