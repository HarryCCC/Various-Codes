import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load the Excel file into a pandas DataFrame
data = pd.read_excel("风险投资组合分析.xlsx")

# Extract the risk-free rate and convert it to daily rate
annual_risk_free_rate = float(data.columns[1])
daily_risk_free_rate = (1 + annual_risk_free_rate/100)**(1/252) - 1

# Extract the time series return data for all stocks
returns_data = data.iloc[1:, 4:].dropna() / 100
returns_data.columns = data.iloc[0, 4:]
# Remove columns where all rows have zero values
returns_data = returns_data.loc[:, (returns_data != 0).any(axis=0)]

# Number of stocks and portfolio simulations
num_stocks = returns_data.shape[1]
num_portfolios = 999999
results = np.zeros((3, num_portfolios))
weights_record = []

# Calculate the average returns and standard deviation for all stocks
avg_returns = returns_data.mean()
std_devs = returns_data.std()

# Calculate the covariance matrix
cov_matrix = returns_data.astype(float).cov()

for i in range(num_portfolios):
    # Randomly assign weights
    weights = np.random.random(num_stocks)
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    # Expected portfolio return
    portfolio_return = np.dot(weights, avg_returns)
    # Expected portfolio volatility
    portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    # Portfolio Sharpe ratio
    sharpe_ratio = (portfolio_return - daily_risk_free_rate) / portfolio_stddev
    
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

# Extract stock names and codes from the Excel file
stock_names_codes = returns_data.columns.values

def save_comprehensive_portfolio_data_with_names_to_txt(stock_names_codes, 
                                                        weights_sharpe_max, weights_std_min, 
                                                        return_sharpe_max, risk_sharpe_max, 
                                                        return_std_min, risk_std_min, 
                                                        filename="投资组合信息.txt"):
    with open(filename, 'w') as file:
        
        # Weights for Optimal Risky Portfolio
        file.write("Optimal Risky Portfolio:\n")
        for name_code, weight in zip(stock_names_codes, weights_sharpe_max):
            file.write(f"{name_code}: {weight*100:.2f}%\n")
        
        # Daily, Monthly, and Annualized return and annualized risk for Optimal Risky Portfolio
        monthly_return_sharpe_max = (1 + return_sharpe_max)**21 - 1
        annualized_return_sharpe_max = (1 + return_sharpe_max)**252 - 1
        annualized_risk_sharpe_max = risk_sharpe_max * np.sqrt(252)
        file.write(f"日化收益率: {return_sharpe_max*100:.2f}%\n")
        file.write(f"月化收益率: {monthly_return_sharpe_max*100:.2f}%\n")
        file.write(f"年化收益率: {annualized_return_sharpe_max*100:.2f}%\n")
        file.write(f"年化风险: {annualized_risk_sharpe_max*100:.2f}%\n\n")  # Additional newline for separation
        
        # Weights for Minimum Variance Portfolio
        file.write("Minimum Variance Portfolio:\n")
        for name_code, weight in zip(stock_names_codes, weights_std_min):
            file.write(f"{name_code}: {weight*100:.2f}%\n")
        
        # Daily, Monthly, and Annualized return and annualized risk for Minimum Variance Portfolio
        monthly_return_std_min = (1 + return_std_min)**21 - 1
        annualized_return_std_min = (1 + return_std_min)**252 - 1
        annualized_risk_std_min = risk_std_min * np.sqrt(252)
        file.write(f"日化收益率: {return_std_min*100:.2f}%\n")
        file.write(f"月化收益率: {monthly_return_std_min*100:.2f}%\n")
        file.write(f"年化收益率: {annualized_return_std_min*100:.2f}%\n")
        file.write(f"年化风险: {annualized_risk_std_min*100:.2f}%\n")
    
    print(f"Data saved to {filename}")

# Now, use the function to save the comprehensive data of the two selected portfolios with stock names, codes, daily, monthly, and annualized percentages to a txt file
save_comprehensive_portfolio_data_with_names_to_txt(stock_names_codes, 
                                                    weights_sharpe_max, weights_std_min, 
                                                    return_sharpe_max, risk_sharpe_max, 
                                                    return_std_min, risk_std_min)




# Plot the capital allocation line and the two portfolios
plt.figure(figsize=(10,7))
plt.scatter(results[1,:], results[0,:], c=results[2,:], cmap='YlGnBu', marker='o')
plt.title('Efficient Frontier with Capital Allocation Line')
plt.xlabel('Portfolio Risk (Standard Deviation)')
plt.ylabel('Portfolio Return')
plt.colorbar(label='Sharpe Ratio')
plt.scatter(risk_std_min,return_std_min,c='red', marker='*', s=100)
plt.scatter(risk_sharpe_max,return_sharpe_max,c='yellow', marker='*', s=100)
plt.plot([0, risk_sharpe_max*2], [daily_risk_free_rate, return_sharpe_max + risk_sharpe_max * (return_sharpe_max - daily_risk_free_rate) / risk_sharpe_max], color='green', linestyle='-', linewidth=2)
plt.legend(['Efficient Frontier','Minimum Variance Portfolio','Optimal Risky Portfolio','Capital Allocation Line'])
plt.grid(True)
plt.show()
