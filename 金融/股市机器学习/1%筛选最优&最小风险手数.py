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

def calculate_test_hands(weights, closing_prices, budget=1000000, shares_per_hand=100):
    """
    Calculate the number of hands to buy for each stock given a budget.
    """
    total_investment = weights * budget
    test_hands = total_investment / (closing_prices * shares_per_hand)
    return np.floor(test_hands)  # Using floor to get whole number of hands

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

# Extract the portfolios with maximum Sharpe ratio and minimum Standard deviation
return_sharpe_max = results[0,results[2].argmax()]
risk_sharpe_max = results[1,results[2].argmax()]
weights_sharpe_max = weights_record[results[2].argmax()]

return_std_min = results[0,results[1].argmin()]
risk_std_min = results[1,results[1].argmin()]
weights_std_min = weights_record[results[1].argmin()]

# Extract stock names and codes from the Excel file
stock_names_codes = returns_data.columns.values

# Load the closing prices from the Excel file
closing_prices = data.iloc[1:, 2].dropna().values

# Select the stocks with weights > 1% from the Optimal Risky Portfolio
indices_selected_stocks_orp = np.where(weights_sharpe_max > 0.01)[0]
selected_weights_sharpe_max = weights_sharpe_max[indices_selected_stocks_orp]
selected_stock_names_codes_orp = stock_names_codes[indices_selected_stocks_orp]

# Normalize the selected weights so they sum up to 1
selected_weights_sharpe_max /= selected_weights_sharpe_max.sum()

# Extract closing prices for the selected stocks in ORP
selected_closing_prices_orp = closing_prices[indices_selected_stocks_orp]

# Similar steps for MVP
indices_selected_stocks_mvp = np.where(weights_std_min > 0.01)[0]
selected_weights_std_min = weights_std_min[indices_selected_stocks_mvp]
selected_stock_names_codes_mvp = stock_names_codes[indices_selected_stocks_mvp]
selected_weights_std_min /= selected_weights_std_min.sum()

selected_closing_prices_mvp = closing_prices[indices_selected_stocks_mvp]

# Calculate hands and adjusted hands for ORP and MVP
index_max_closing_price_orp = np.argmax(selected_closing_prices_orp)
max_closing_price_orp = selected_closing_prices_orp[index_max_closing_price_orp]
max_closing_price_weight_orp = selected_weights_sharpe_max[index_max_closing_price_orp]
total_price_orp = max_closing_price_orp / max_closing_price_weight_orp
hands_orp = np.where(selected_closing_prices_orp != 0, (selected_weights_sharpe_max * total_price_orp) / selected_closing_prices_orp, 0)
hands_orp[index_max_closing_price_orp] = 1
adjustment_multiplier_orp = 1 / hands_orp.min()
adjusted_hands_orp = hands_orp * adjustment_multiplier_orp

index_max_closing_price_mvp = np.argmax(selected_closing_prices_mvp)
max_closing_price_mvp = selected_closing_prices_mvp[index_max_closing_price_mvp]
max_closing_price_weight_mvp = selected_weights_std_min[index_max_closing_price_mvp]
total_price_mvp = max_closing_price_mvp / max_closing_price_weight_mvp
hands_mvp = np.where(selected_closing_prices_mvp != 0, (selected_weights_std_min * total_price_mvp) / selected_closing_prices_mvp, 0)
hands_mvp[index_max_closing_price_mvp] = 1
adjustment_multiplier_mvp = 1 / hands_mvp.min()
adjusted_hands_mvp = hands_mvp * adjustment_multiplier_mvp

# Calculate test hands for ORP and MVP
test_hands_orp = calculate_test_hands(selected_weights_sharpe_max, selected_closing_prices_orp)
test_hands_mvp = calculate_test_hands(selected_weights_std_min, selected_closing_prices_mvp)

# Append the test hand information to the TXT file
with open("predict/1%筛选投资组合手数.txt", "w") as file:
    file.write("Optimal Risky Portfolio (ORP):")
    for name_code, weight, closing_price, adjusted_hands, test_hand in zip(selected_stock_names_codes_orp, selected_weights_sharpe_max, selected_closing_prices_orp, adjusted_hands_orp, test_hands_orp):
        file.write(f"{name_code}: Weight={weight*100:.2f}%, Closing Price={closing_price:.2f}, Adjusted Hands={adjusted_hands:.2f}, Test Hands={test_hand}\n")
    file.write(f"ORP Expected Return: {return_sharpe_max*100:.2f}%\n")
    file.write(f"ORP Risk (Standard Deviation): {risk_sharpe_max*100:.2f}%\n")

    file.write("\nMinimum Variance Portfolio (MVP):\n")
    for name_code, weight, closing_price, adjusted_hands, test_hand in zip(selected_stock_names_codes_mvp, selected_weights_std_min, selected_closing_prices_mvp, adjusted_hands_mvp, test_hands_mvp):
        file.write(f"{name_code}: Weight={weight*100:.2f}%, Closing Price={closing_price:.2f}, Adjusted Hands={adjusted_hands:.2f}, Test Hands={test_hand}\n")
    file.write(f"MVP Expected Return: {return_std_min*100:.2f}%\n")
    file.write(f"MVP Risk (Standard Deviation): {risk_std_min*100:.2f}%\n")