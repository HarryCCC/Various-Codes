import os
import pandas as pd

# Change the default directory path to your desktop
desktop_path = "C:/Users/11470/Desktop"
os.chdir(desktop_path)

# List of excel files to be combined
files = ["1.xlsx", "2.xlsx", "3.xlsx"]

# Combine the first two excel files
df1 = pd.read_excel(files[0])
df2 = pd.read_excel(files[1])
combined_df = pd.concat([df1, df2], axis=1)

# Combine the rest of the excel files with the combined dataframe
for i in range(2, len(files)):
    df = pd.read_excel(files[i])
    combined_df = pd.concat([combined_df, df], axis=1)

# Save the combined dataframe to a new excel file
combined_df.to_excel("combined_files.xlsx", index=False)
