from pydub import AudioSegment
import os

def normalize_audio_volume(directory_path, target_dBFS=-20.0):
    # 确保输出目录存在
    output_directory = os.path.join(directory_path, "Musics_normalized")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # 列出目录中的所有mp3文件
    files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]
    audio_segments = []

    # 加载音频文件
    total_files = len(files)
    for index, file in enumerate(files, start=1):
        audio_path = os.path.join(directory_path, file)
        print(f"Loading {index}/{total_files}: {file}")
        audio = AudioSegment.from_file(audio_path)
        audio_segments.append(audio)

    # 调整每个音频的音量到目标dBFS并处理文件名
    for index, (audio, file) in enumerate(zip(audio_segments, files), start=1):
        # 处理文件名，去除作者名
        new_name = file.split(' - ')[-1]  # 假设文件名格式为 '作者名 - 歌曲名.mp3'
        normalized_audio = audio.apply_gain(target_dBFS - audio.dBFS)
        output_path = os.path.join(output_directory, new_name)
        normalized_audio.export(output_path, format='mp3')
        print(f"Processing {index}/{total_files}: {file} normalized to {new_name}")

# 使用函数
normalize_audio_volume('Musics')
