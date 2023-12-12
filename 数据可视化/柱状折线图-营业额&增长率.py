import matplotlib.pyplot as plt
import numpy as np
import random

years = np.arange(2018,2025)
#Manually input the revenue values for each year
revenue = np.array([83,105,125,158,182,223,261])
#Calculate the growth rate
growth_rate = np.concatenate(([np.nan],np.diff(revenue) / revenue[:-1]))

# Create the figure and axes
fig, ax1 = plt.subplots()

# Create the line chart for growth rate
line_color = plt.get_cmap('viridis')(random.random())
ax1.plot(years, growth_rate, color=line_color, marker='*', alpha=1)
ax1.set_xlabel('Year')
ax1.set_ylabel('Growth Rate', color=line_color)
ax1.tick_params('y', colors=line_color)

# Add star and values to growth rate line
for i, value in enumerate(growth_rate):
    ax1.text(years[i], value, f'({round(value, 2)})', ha='center', va='bottom')


# Create the bar chart for revenue
bar_color = plt.get_cmap('plasma')(random.random())
ax2 = ax1.twinx()
ax2.bar(years, revenue, color=bar_color, alpha=0.5)
ax2.set_ylabel('Revenue($m)', color=bar_color)
ax2.tick_params('y', colors=bar_color)

# Add values to revenue bar chart
for i, value in enumerate(revenue):
    ax2.text(years[i]-0.2, value+5, str(value), ha='center', va='bottom')

# Add title and show the plot
plt.title('Company Revenue')
plt.show()
