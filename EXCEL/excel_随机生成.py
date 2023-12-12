import pandas as pd
import random
import os

def generate_excel_file(file_name, sheet_name, num_rows, num_columns):
    '''
    This function generates a random excel file with the specified number of rows and columns.
    
    file_name: string
        The name of the excel file
        
    sheet_name: string
        The name of the sheet in the excel file
        
    num_rows: int
        The number of rows in the sheet
        
    num_columns: int
        The number of columns in the sheet
    '''
    # Create a dataframe with random data
    data = {f"Column {i}": [random.randint(1, 100) for j in range(num_rows)] for i in range(num_columns)}
    df = pd.DataFrame(data)
    
    # Write the dataframe to an excel file
    writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()

# Change the default directory path to the desktop
os.chdir(r"C:\Users\11470\Desktop")

# Generate three random excel files
for i in range(3):
    file_name = f"{i+1}.xlsx"
    sheet_name = f"Sheet{i+1}"
    generate_excel_file(file_name, sheet_name, 100, 5)
