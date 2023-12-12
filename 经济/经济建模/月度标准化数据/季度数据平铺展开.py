import os
import pandas as pd
import glob

# Function to expand quarterly data with corrected column name handling
def expand_quarterly_csv_file_corrected(file_path):
    # Read the first line of the file to capture the original file name or header
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    
    try:
        # Reload the CSV file, this time we don't skip the first row since it contains valid data
        df = pd.read_csv(file_path, skiprows=1, names=['date', 'value'])
    except pd.errors.EmptyDataError:
        print(f"Skipping empty file: {file_path}")
        return
    
    # Drop the first row if it contains headers
    if df.iloc[0, 0] == 'date':
        df = df.iloc[1:].reset_index(drop=True)
    
    # Create an empty DataFrame to hold the expanded data
    expanded_df = pd.DataFrame(columns=['date', 'value'])

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        year, month = row['date'].split('-')  # Extract the year and the month from the 'date' column
        value = row['value']  # Extract the value for that quarter

        # Determine which months belong to the given quarter
        if month == '06':
            quarter_months = ['04', '05', '06']
        elif month == '09':
            quarter_months = ['07', '08', '09']
        elif month == '12':
            quarter_months = ['10', '11', '12']
        elif month == '03':
            quarter_months = ['01', '02', '03']
        
        # Create new date strings for each month in the quarter and append to the expanded DataFrame
        for quarter_month in quarter_months:
            new_date = f"{year}-{quarter_month}"
            expanded_df = expanded_df._append({'date': new_date, 'value': value}, ignore_index=True)

    # Define the path for the new CSV file
    base_name = os.path.basename(file_path)
    expanded_file_name = os.path.splitext(base_name)[0] + '_expanded.csv'
    expanded_file_path = os.path.join("/mnt/data", expanded_file_name)

    # Save the expanded DataFrame to a new CSV file, including the original first line
    with open(expanded_file_path, 'w') as f:
        f.write(first_line + '\n')
    expanded_df.to_csv(expanded_file_path, mode='a', index=False)

# Define the directory where the CSV files are located
csv_directory = "./"

# Get a list of all CSV files in the directory
csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))

# Process each CSV file
for csv_file in csv_files:
    expand_quarterly_csv_file_corrected(csv_file)
