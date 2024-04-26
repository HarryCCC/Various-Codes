import requests
import os

# 设置用户代理
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# MIDI文件将被保存的本地文件夹路径
local_folder_path = "D:\\MIDI"

# 确保本地文件夹存在
if not os.path.exists(local_folder_path):
    os.makedirs(local_folder_path)

# 尝试下载的MIDI文件的范围
midi_range = range(1, 10001)

# 尝试下载MIDI文件
for i in midi_range:
    download_url = f'https://bitmidi.com/uploads/{i}.mid'
    local_filename = os.path.join(local_folder_path, f'{i}.mid')

    # 尝试下载MIDI文件
    try:
        response = requests.get(download_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(response.content)
            print(f'Successfully downloaded {local_filename}')
        else:
            print(f'File not found: {download_url}')
    except requests.exceptions.RequestException as e:
        print(f'Failed to download {download_url}. Error: {e}')

