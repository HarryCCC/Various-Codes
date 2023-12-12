import os

def count_sub_files(directory):
    """Counts the number of sub-files in the given directory, including files in subdirectories."""
    file_count = 0

    for root, dirs, files in os.walk(directory):
        file_count += len(files)

    return file_count

# Using the current directory
current_directory = os.getcwd()
file_count = count_sub_files(current_directory)

print(file_count)
input("let me out!!!")

