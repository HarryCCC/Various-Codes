import pandas as pd

def merge_excel_sheets(file_path, sheets, output_file):
    '''
    This function merges multiple excel sheets into one excel file.
    
    file_path: string
        The path of the excel file
        
    sheets: list of strings
        List of sheet names to be merged
        
    output_file: string
        The name of the output file
    '''
    # Create an empty dataframe
    merged_df = pd.DataFrame()
    
    # Read each sheet and append it to the merged dataframe
    for sheet in sheets:
        df = pd.read_excel(file_path, sheet_name=sheet)
        merged_df = merged_df.append(df, ignore_index=True)
        
    # Write the merged dataframe to an excel file
    merged_df.to_excel(output_file, index=False)
    
    return "Merging Completed!"



import os
import pandas as pd

# Change the default directory path to your desktop
desktop_path = "C:/Users/11470/Desktop"
os.chdir(desktop_path)

# List of excel files to be combined
files = ["1.xlsx", "2.xlsx", "3.xlsx"]

# Combine the excel files into a single dataframe
combined_df = pd.concat([pd.read_excel(f) for f in files])

# Save the combined dataframe to a new excel file
combined_df.to_excel("combined_files.xlsx", index=False)
