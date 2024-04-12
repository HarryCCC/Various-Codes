import pandas as pd
import numpy as np

# Read the Excel data
df = pd.read_excel('FINM3008 - Assignment Data Analysis S1 2024.xlsx', sheet_name='Qtr Returns', index_col=0)

# Remove the first row
df = df.iloc[1:]

# Convert data to numeric type, non-numeric values to NaN
df = df.apply(pd.to_numeric, errors='coerce')

# Calculate the covariance matrix
cov_matrix = df.cov()

# Save the covariance matrix to a txt file
np.savetxt('covariance_matrix.txt', cov_matrix, delimiter='\t')

print("Covariance matrix saved to 'covariance_matrix.txt'.")