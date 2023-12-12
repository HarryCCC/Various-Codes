import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load the Excel file into a pandas DataFrame
data = pd.read_excel("Data_Assignment_finm2003_2023s2.xlsx")

# Given risk-free rate
risk_free_rate = 0.003

# Number of portfolio simulations
num_portfolios = 100000
results = np.zeros((3, num_portfolios))
weights_record = []

# Calculate the average returns and standard deviation for both stocks
sibvq_avg_return = data['Returns'].mean()
sibvq_std_dev = data['Returns'].std()
bac_avg_return = data['Returns.1'].mean()
bac_std_dev = data['Returns.1'].std()

# Calculate the covariance using the correlation coefficient and standard deviations
correlation = data['Correlation'].iloc[0]
covariance = correlation * sibvq_std_dev * bac_std_dev

for i in range(num_portfolios):
    # Randomly assign weights
    weights = np.random.random(2)
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    # Expected portfolio return
    portfolio_return = weights[0] * sibvq_avg_return + weights[1] * bac_avg_return
    # Expected portfolio volatility
    portfolio_stddev = np.sqrt(weights[0]**2 * sibvq_std_dev**2 + weights[1]**2 * bac_std_dev**2 + 2 * weights[0] * weights[1] * covariance)
    # Portfolio Sharpe ratio
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_stddev
    
    results[0,i] = portfolio_return
    results[1,i] = portfolio_stddev
    results[2,i] = sharpe_ratio

# Extract the portfolios with maximum Sharpe ratio & minimum Standard deviation
return_sharpe_max = results[0,results[2].argmax()]
risk_sharpe_max = results[1,results[2].argmax()]

return_std_min = results[0,results[1].argmin()]
risk_std_min = results[1,results[1].argmin()]

# Weights for the two portfolios
weights_sharpe_max = weights_record[results[2].argmax()]
weights_std_min = weights_record[results[1].argmin()]

# Define the range for x and y axis to zoom in on the desired part of the efficient frontier
x_limit = [0.065, 0.125]  # Define the range for x-axis (Portfolio Risk)
y_limit = [0.0075, 0.0090]  # Define the range for y-axis (Portfolio Return)

# Plot the zoomed-in capital allocation line and the two portfolios
plt.figure(figsize=(10,7))
plt.scatter(results[1,:], results[0,:], c=results[2,:], cmap='YlGnBu', marker='o')
plt.title('Efficient Frontier with Capital Allocation Line')
plt.xlabel('Portfolio Risk (Standard Deviation)')
plt.ylabel('Portfolio Return')
plt.colorbar(label='Sharpe Ratio')
plt.scatter(risk_std_min,return_std_min,c='red', marker='*', s=100)
plt.scatter(risk_sharpe_max,return_sharpe_max,c='yellow', marker='*', s=100)
plt.plot([0, risk_sharpe_max*2], [risk_free_rate, return_sharpe_max + risk_sharpe_max * (return_sharpe_max - risk_free_rate) / risk_sharpe_max], color='green', linestyle='-', linewidth=2)
plt.xlim(x_limit)
plt.ylim(y_limit)
plt.legend(['Efficient Frontier','Minimum Variance Portfolio','Optimal Risky Portfolio','Capital Allocation Line'])
plt.grid(True)
plt.show()

print(weights_sharpe_max, weights_std_min, return_sharpe_max, risk_sharpe_max, return_std_min, risk_std_min)




'''
# Compute weights for the minimum variance portfolio
w_svb_min_var = (bac_std_dev**2 - covariance) / (sibvq_std_dev**2 + bac_std_dev**2 - 2 * covariance)
w_bac_min_var = 1 - w_svb_min_var

# Compute the standard deviation for the minimum variance portfolio
std_dev_min_var = np.sqrt(w_svb_min_var**2 * sibvq_std_dev**2 + w_bac_min_var**2 * bac_std_dev**2 + 2 * w_svb_min_var * w_bac_min_var * covariance)

# Compute the expected return for the minimum variance portfolio
return_min_var = w_svb_min_var * sibvq_avg_return + w_bac_min_var * bac_avg_return

# Compute weights for the optimal risky portfolio (maximizing the Sharpe Ratio)
denominator = (sibvq_avg_return - risk_free_rate) * bac_std_dev**2 + (bac_avg_return - risk_free_rate) * sibvq_std_dev**2 - (sibvq_avg_return + bac_avg_return - 2*risk_free_rate) * covariance
w_svb_optimal = ((sibvq_avg_return - risk_free_rate) * bac_std_dev**2 - (bac_avg_return - risk_free_rate) * covariance) / denominator
w_bac_optimal = 1 - w_svb_optimal

# Compute the standard deviation for the optimal risky portfolio
std_dev_optimal = np.sqrt(w_svb_optimal**2 * sibvq_std_dev**2 + w_bac_optimal**2 * bac_std_dev**2 + 2 * w_svb_optimal * w_bac_optimal * covariance)

# Compute the expected return for the optimal risky portfolio
return_optimal = w_svb_optimal * sibvq_avg_return + w_bac_optimal * bac_avg_return

w_svb_min_var, w_bac_min_var, std_dev_min_var, return_min_var, w_svb_optimal, w_bac_optimal, std_dev_optimal, return_optimal


'''