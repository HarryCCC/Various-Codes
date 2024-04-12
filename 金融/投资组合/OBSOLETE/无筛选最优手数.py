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

# Extract the portfolios with maximum Sharpe ratio
return_sharpe_max = results[0,results[2].argmax()]
risk_sharpe_max = results[1,results[2].argmax()]

# Weights for the Optimal Risky Portfolio
weights_sharpe_max = weights_record[results[2].argmax()]

# Extract stock names and codes from the Excel file
stock_names_codes = returns_data.columns.values

# Select the stocks with weights > 0.1% from the Optimal Risky Portfolio
indices_selected_stocks = np.where(weights_sharpe_max > 0.001)[0]
selected_weights_sharpe_max = weights_sharpe_max[indices_selected_stocks]
selected_stock_names_codes = stock_names_codes[indices_selected_stocks]

# Normalize the selected weights so they sum up to 1
selected_weights_sharpe_max /= selected_weights_sharpe_max.sum()

# Calculate returns and risks for the newly weighted selected stocks
selected_avg_returns = avg_returns.iloc[indices_selected_stocks].values
selected_cov_matrix = cov_matrix.iloc[indices_selected_stocks, indices_selected_stocks]

selected_portfolio_return = np.dot(selected_weights_sharpe_max, selected_avg_returns)
selected_portfolio_stddev = np.sqrt(np.dot(selected_weights_sharpe_max.T, np.dot(selected_cov_matrix, selected_weights_sharpe_max)))

# Load the closing prices from the Excel file
closing_prices = data.iloc[1:, 2].dropna().values

# Extract closing prices for the selected stocks
selected_closing_prices = closing_prices[indices_selected_stocks]


'''
收盘价*手数=单价，单价/总价=权重。这样我们就得到了权重，手数，收盘价的关系！
也就是收盘价*手数/总价=权重。这里我们代入收盘价最高的那支股票的收盘价和权重，其对应的手数就是1，就能得到总价。
然后，就能用总价，收盘价，权重，计算出其他股票的手数！
'''

# 1. Find the stock with the highest closing price among the selected stocks
index_max_closing_price = np.argmax(selected_closing_prices)
max_closing_price_stock = selected_stock_names_codes[index_max_closing_price]
max_closing_price = selected_closing_prices[index_max_closing_price]
max_closing_price_weight = selected_weights_sharpe_max[index_max_closing_price]

# 2. Assume the hands for the stock with the highest closing price is 1
hands_max_closing_price = 1
total_price = max_closing_price / max_closing_price_weight

# 3. Calculate hands for other stocks
# Here, we'll ensure we do not divide by zero. If closing price is zero, we'll set the hands to zero.
hands_other_stocks = np.where(selected_closing_prices != 0, (selected_weights_sharpe_max * total_price) / selected_closing_prices, 0)
hands_other_stocks[index_max_closing_price] = 1  # Correcting the hands for the stock with the highest closing price

# Now, let's apply the adjustment.
adjustment_multiplier = 1 / hands_other_stocks.min()
adjusted_hands = hands_other_stocks * adjustment_multiplier

# Create a dataframe to show the results
df_hands = pd.DataFrame({
    'Stock': selected_stock_names_codes,
    'Weight (%)': selected_weights_sharpe_max * 100,
    'Closing Price': selected_closing_prices,
    'Hands': hands_other_stocks,
    'Adjusted Hands': adjusted_hands
})

print(df_hands)


# Save the dataframe to a TXT file
with open("无筛选最优手数.txt", "w") as file:
    file.write("Selected Stocks Information:\n\n")
    for index, row in df_hands.iterrows():
        file.write(f"Stock: {row['Stock']} | Weight: {row['Weight (%)']:.2f}% | Closing Price: {row['Closing Price']:.2f} | Hands: {row['Hands']:.2f} | Adjusted Hands: {row['Adjusted Hands']:.2f}\n")
    file.write("\n")
    # Add the daily return to the file
    file.write(f"日化收益率: {selected_portfolio_return*100:.2f}%\n")
    file.write("\n")  # Add an additional newline for separation