import subprocess
import re
import os
import psutil
import platform

# Set the full path to ffmpeg
FFMPEG_PATH = r"D:\SOFTWARES\ffmpeg\bin\ffmpeg.exe"

def parse_ffmpeg_output(output):
    bitrate_pattern = re.compile(r'bitrate:\s+(\d+)\s+kb/s')
    fps_pattern = re.compile(r'(\d+(?:\.\d+)?)\s+fps')
    
    bitrate = None
    frame_rate = None
    
    for line in output.splitlines():
        if not bitrate:
            bitrate_match = bitrate_pattern.search(line)
            if bitrate_match:
                bitrate = int(bitrate_match.group(1))
        
        if not frame_rate:
            fps_match = fps_pattern.search(line)
            if fps_match:
                frame_rate = float(fps_match.group(1))
    
    return bitrate, frame_rate

def is_gpu_available():
    try:
        if platform.system() == "Windows":
            subprocess.run(['nvidia-smi'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        elif platform.system() == "Darwin":
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True)
            return 'Metal' in result.stdout
        else:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            return any(x in result.stdout.lower() for x in ['nvidia', 'amd', 'intel', 'gpu', 'vga'])
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def compress_video(input_file, compression_ratio=0.5, frame_rate=None, use_gpu=False, max_usage=0.8):
    # 创建带有"_Compressed"后缀的输出文件名
    filename, ext = os.path.splitext(input_file)
    output_file = f"{filename}_Compressed{ext}"
    
    # 获取输入视频信息
    probe_command = [FFMPEG_PATH, '-i', input_file, '-hide_banner']
    result = subprocess.run(probe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    bitrate, original_frame_rate = parse_ffmpeg_output(result.stderr)
    
    if bitrate is None or original_frame_rate is None:
        print(f"无法获取视频信息：{input_file}")
        return

    # 计算目标比特率
    target_bitrate = int(bitrate * compression_ratio)
    
    ffmpeg_command = [
        FFMPEG_PATH,
        '-i', input_file,
        '-b:v', f'{target_bitrate}k',
    ]

    # 调整帧率
    if frame_rate and original_frame_rate > frame_rate:
        ffmpeg_command.extend(['-r', str(frame_rate)])

    # 检查GPU可用性
    gpu_available = is_gpu_available()

    if use_gpu and gpu_available:
        ffmpeg_command.extend(['-vcodec', 'h264_nvenc'])
    else:
        ffmpeg_command.extend(['-vcodec', 'libx264'])
        use_gpu = False  # 如果GPU不可用，设置为False

    # 如果使用CPU编码，设置CPU线程数
    if not use_gpu:
        cpu_count = psutil.cpu_count()
        cpu_threads = max(1, int(cpu_count * max_usage))
        ffmpeg_command.extend(['-threads', str(cpu_threads)])
    
    ffmpeg_command.append(output_file)

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"视频压缩成功：{output_file}")
    except subprocess.CalledProcessError as e:
        print(f"压缩视频时出错 {input_file}: {e}")

def is_video_file(filename):
    """检查文件是否为视频文件"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp']
    _, ext = os.path.splitext(filename)
    return ext.lower() in video_extensions

def process_videos(directory, compression_ratio=0.5, frame_rate=None, use_gpu=False, max_usage=0.8):
    processed_count = 0
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and is_video_file(filename) and not filename.endswith('_Compressed.mp4'):
            print(f"正在处理视频: {filename}")
            compress_video(filepath, compression_ratio, frame_rate, use_gpu, max_usage)
            processed_count += 1
    
    if processed_count == 0:
        print("当前目录未找到可处理的视频文件")
    else:
        print(f"共处理了 {processed_count} 个视频文件")

if __name__ == "__main__":
    directory = "."  # 当前目录，根据需要修改
    compression_ratio = 0.1  # 压缩比例
    frame_rate = 30  # 目标帧率
    use_gpu = True  # 是否使用GPU
    max_usage = 0.6  # CPU或GPU的最大使用率

    process_videos(directory, compression_ratio, frame_rate, use_gpu, max_usage)