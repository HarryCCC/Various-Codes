import subprocess
import re

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

def compress_video(input_file, compression_ratio=0.5, frame_rate=None, use_gpu=False):
    output_file = input_file.replace('.mp4', '_compressed.mp4')
    
    # 获取输入视频的信息
    probe_command = [
        'ffmpeg', '-i', input_file, '-hide_banner'
    ]
    result = subprocess.run(probe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    bitrate, original_frame_rate = parse_ffmpeg_output(result.stderr)
    
    if bitrate is None or original_frame_rate is None:
        print("Failed to retrieve video information.")
        return

    # 计算目标比特率
    target_bitrate = int(bitrate * compression_ratio)
    
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-b:v', f'{target_bitrate}k',  # 设置目标比特率
    ]

    # 调整帧率
    if frame_rate and original_frame_rate > frame_rate:
        ffmpeg_command.extend(['-r', str(frame_rate)])  # 降低帧率

    if use_gpu:
        ffmpeg_command.extend(['-vcodec', 'h264_nvenc'])  # 使用NVIDIA显卡的H.264编码器
    else:
        ffmpeg_command.extend(['-vcodec', 'libx264'])  # 使用软件编码器
    
    ffmpeg_command.append(output_file)

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Compressed video saved as {output_file}")
    except subprocess.CalledProcessError as e:
        if use_gpu:
            print("Failed to use GPU for compression.")
            continue_with_cpu = input("Do you want to continue with CPU instead? (Y/N): ")
            if continue_with_cpu.lower() == 'y':
                compress_video(input_file, compression_ratio, frame_rate, use_gpu=False)
            else:
                print("Compression aborted.")
        else:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    input_video = "video.mp4"
    compression_ratio = 0.1 # 压缩比率，0-1之间，1表示比特率不变，0.5表示比特率为原来的0.5倍
    frame_rate = 30  # 指定压缩后的帧率，如无需要可以设置为None
    use_gpu = True  # 设置为True以使用GPU，否则设置为False

    compress_video(input_video, compression_ratio, frame_rate, use_gpu)
