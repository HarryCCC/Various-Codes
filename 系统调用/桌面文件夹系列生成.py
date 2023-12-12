import os

desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

for i in range(1, 13):
    week_folder_name = f'WEEK{i}'
    week_folder_path = os.path.join(desktop_path, week_folder_name)
    os.makedirs(week_folder_path, exist_ok=True)
