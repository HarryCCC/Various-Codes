import os
import pandas as pd
import glob

def expand_csv_file(file_path):
    # Read the first line of the file to capture the original file name or header
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    
    try:
        # Reload the CSV file, skipping the first row to fix the header issue
        df = pd.read_csv(file_path, skiprows=1)
    except pd.errors.EmptyDataError:
        print(f"Skipping empty file: {file_path}")
        return

    # Rename the columns to make them more understandable
    df.columns = ['date', 'value']

    # Create an empty DataFrame to hold the expanded data
    expanded_df = pd.DataFrame(columns=['date', 'value'])

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        year = row['date'].split('-')[0]  # Extract the year from the 'date' column
        value = row['value']  # Extract the value for that year
        for month in range(1, 13):  # Iterate through each month (1 to 12)
            new_date = f"{year}-{str(month).zfill(2)}"  # Create a new date string
            expanded_df = expanded_df._append({'date': new_date, 'value': value}, ignore_index=True)

    # Define the path for the new CSV file
    base_name = os.path.basename(file_path)
    expanded_file_name = os.path.splitext(base_name)[0] + '_expanded.csv'
    expanded_file_path = os.path.join(os.path.dirname(file_path), expanded_file_name)

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
    expand_csv_file(csv_file)
