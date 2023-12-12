import os
import csv
import pandas as pd
from datetime import datetime
from collections import defaultdict

# Function to merge multiple CSV files into one, within a specified date range
def merge_csv_files(csv_files, output_file_path, latest_start_date_str, earliest_end_date_str):
    merged_data_dict = defaultdict(lambda: [None] * len(csv_files))
    merged_header = ['date']

    for idx, csv_file in enumerate(csv_files):
        df = pd.read_csv(os.path.join(folder_path, csv_file), skiprows=1, names=['date', 'value'])
        
        with open(os.path.join(folder_path, csv_file), 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            header = next(reader)
            merged_header.extend([f"{csv_file[:-4]}_{header[1]}"])

        df_filtered = df[(df['date'] >= latest_start_date_str) & (df['date'] <= earliest_end_date_str)]
        
        for _, row in df_filtered.iterrows():
            date = row['date']
            values = [row['value']]
            if merged_data_dict[date][idx] is None:
                merged_data_dict[date][idx] = values
            else:
                merged_data_dict[date][idx].extend(values)
                
    merged_data_list = [[date] + [val for sublist in values for val in (sublist if sublist is not None else [None])] 
                        for date, values in sorted(merged_data_dict.items())]
    
    with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(merged_header)
        writer.writerows(merged_data_list)

# Set the folder path to the current directory or wherever your CSV files are located
folder_path = '.'  # Current directory

# Get the list of all CSV files in the directory
all_csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize variables to find the latest start date and earliest end date
latest_start_date = datetime.min
earliest_end_date = datetime.max

# Find the latest start date and earliest end date from all CSV files
for csv_file in all_csv_files:
    df = pd.read_csv(os.path.join(folder_path, csv_file), skiprows=1)
    start_date_str = df.iloc[0, 0]
    end_date_str = df.iloc[-1, 0]
    
    start_date = datetime.strptime(start_date_str, '%Y-%m')
    end_date = datetime.strptime(end_date_str, '%Y-%m')
    
    latest_start_date = max(latest_start_date, start_date)
    earliest_end_date = min(earliest_end_date, end_date)

latest_start_date_str = latest_start_date.strftime('%Y-%m')
earliest_end_date_str = earliest_end_date.strftime('%Y-%m')

# Create a directory to store the final merged CSV files
output_directory = './合并数据'
os.makedirs(output_directory, exist_ok=True)

# Merge all CSV files within the date range and save the final merged CSV file
output_file_path = os.path.join(output_directory, "合并数据.csv")
merge_csv_files(all_csv_files, output_file_path, latest_start_date_str, earliest_end_date_str)
