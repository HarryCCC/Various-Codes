import subprocess
import re
import os
import psutil
import platform

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
    output_file = input_file.replace('.mp4', '_compressed.mp4')
    
    # Get input video information
    probe_command = ['ffmpeg', '-i', input_file, '-hide_banner']
    result = subprocess.run(probe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    bitrate, original_frame_rate = parse_ffmpeg_output(result.stderr)
    
    if bitrate is None or original_frame_rate is None:
        print(f"Failed to retrieve video information for {input_file}.")
        return

    # Calculate target bitrate
    target_bitrate = int(bitrate * compression_ratio)
    
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-b:v', f'{target_bitrate}k',
    ]

    # Adjust frame rate
    if frame_rate and original_frame_rate > frame_rate:
        ffmpeg_command.extend(['-r', str(frame_rate)])

    # Check GPU availability
    gpu_available = is_gpu_available()

    if use_gpu and gpu_available:
        ffmpeg_command.extend(['-vcodec', 'h264_nvenc'])
    else:
        ffmpeg_command.extend(['-vcodec', 'libx264'])
        use_gpu = False  # Set to False if GPU is not available

    # Set CPU threads if using CPU encoding
    if not use_gpu:
        cpu_count = psutil.cpu_count()
        cpu_threads = max(1, int(cpu_count * max_usage))
        ffmpeg_command.extend(['-threads', str(cpu_threads)])
    
    ffmpeg_command.append(output_file)

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Compressed video saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while compressing {input_file}: {e}")

def process_videos(directory, compression_ratio=0.5, frame_rate=None, use_gpu=False, max_usage=0.8):
    video_pattern = re.compile(r'video\d+\.mp4')
    
    for filename in os.listdir(directory):
        if video_pattern.match(filename):
            input_file = os.path.join(directory, filename)
            compress_video(input_file, compression_ratio, frame_rate, use_gpu, max_usage)

if __name__ == "__main__":
    directory = "."  # Current directory, change if needed
    compression_ratio = 0.1
    frame_rate = 30
    use_gpu = True
    max_usage = 0.6  # 80% maximum usage of CPU or GPU

    process_videos(directory, compression_ratio, frame_rate, use_gpu, max_usage)