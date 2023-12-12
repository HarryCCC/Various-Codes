initial_investment = 127797020  
annual_return = 27750216    
discount_rate = 0.036   
days_in_year = 365
growth_rate = 0.02  # 2% annual growth rate for net cash inflow
project_lifetime = 15  
initial_capital_investment = 100000000
residual_value_percentage = 0.20  # 20% of initial capital investment

# Initialize variables
cumulative_discounted_cashflow = 0
t = 0

# Iterate over the years to calculate the discounted payback period with growth rate
while cumulative_discounted_cashflow < initial_investment:
    t += 1
    discounted_cashflow = annual_return * (1 + growth_rate)**(t-1) / (1 + discount_rate)**t
    cumulative_discounted_cashflow += discounted_cashflow

# Calculate the exact time within the final year
fractional_year = (initial_investment - (cumulative_discounted_cashflow - discounted_cashflow)) / discounted_cashflow
t -= (1 - fractional_year)

# Convert the time to days
days_to_recover = t * days_in_year

# Calculate the number of years, months, and days from the total days
years = int(days_to_recover // days_in_year)
remaining_days = days_to_recover % days_in_year

months = int(remaining_days // 30.44)  # Using an average month length of 30.44 days
remaining_days %= 30.44

days = int(remaining_days)

PBP_output = f"Discounted Payback Period: {years} years, {months} months, {days} days (total {int(days_to_recover)} days)"
print(PBP_output)


# Calculate the residual value of the asset after 15 years
residual_value = initial_capital_investment * residual_value_percentage

# Calculate the NPV of all future cash flows including the residual value
total_discounted_cashflows = 0
for year in range(1, project_lifetime + 1):
    if year == project_lifetime:  # add the residual value in the last year
        cashflow = annual_return * (1 + growth_rate)**(year-1) + residual_value
    else:
        cashflow = annual_return * (1 + growth_rate)**(year-1)
    total_discounted_cashflows += cashflow / (1 + discount_rate)**year

# Calculate ROI
net_profit = total_discounted_cashflows - initial_investment
ROI = (net_profit / initial_investment) * 100

ROI_output = f"Return of Investment: {ROI:.2f}%"
print(ROI_output)