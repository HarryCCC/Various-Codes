import subprocess
import re
import os
import psutil
import platform
import sys

# 设置ffmpeg的完整路径
FFMPEG_PATH = r"D:\SOFTWARES\ffmpeg\bin\ffmpeg.exe"

def parse_ffmpeg_output(output):
    """解析FFmpeg输出，提取比特率和帧率信息"""
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

def test_gpu_encoding():
    """测试GPU编码是否可用"""
    print("测试GPU编码功能是否可用...")
    try:
        # 创建一个1秒的测试视频命令
        test_cmd = [
            FFMPEG_PATH, 
            "-f", "lavfi", 
            "-i", "color=c=black:s=1280x720:r=30:d=1", 
            "-c:v", "h264_nvenc", 
            "-f", "null", 
            "-"
        ]
        
        # 尝试运行命令
        result = subprocess.run(
            test_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            timeout=10  # 设置超时
        )
        
        # 检查是否成功
        if result.returncode == 0:
            print("GPU编码功能正常可用")
            return True
        else:
            # 检查常见的GPU错误信息
            if "nvenc API version" in result.stderr or "required Nvidia driver" in result.stderr:
                print("NVIDIA驱动版本过低，需要更新驱动")
            elif "No NVENC capable devices found" in result.stderr:
                print("未找到支持NVENC的NVIDIA设备")
            else:
                print(f"GPU编码测试失败，错误信息：{result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("GPU编码测试超时")
        return False
    except Exception as e:
        print(f"GPU编码测试出错：{e}")
        return False

def is_gpu_available():
    """检查系统是否有可用的GPU"""
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
    """压缩视频文件，支持GPU和CPU编码，自动降级"""
    # 创建带有"_Compressed"后缀的输出文件名
    filename, ext = os.path.splitext(input_file)
    output_file = f"{filename}_Compressed{ext}"
    
    # 获取输入视频信息
    probe_command = [FFMPEG_PATH, '-i', input_file, '-hide_banner']
    try:
        result = subprocess.run(
            probe_command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8',
            timeout=60
        )
    except subprocess.TimeoutExpired:
        print(f"分析视频超时：{input_file}，跳过此文件")
        return False
    except Exception as e:
        print(f"分析视频出错：{input_file}，错误: {e}")
        return False
        
    bitrate, original_frame_rate = parse_ffmpeg_output(result.stderr)
    
    if bitrate is None or original_frame_rate is None:
        print(f"无法获取视频信息：{input_file}，跳过此文件")
        return False

    # 计算目标比特率
    target_bitrate = int(bitrate * compression_ratio)
    
    # 检查GPU可用性和用户设置
    gpu_enabled = use_gpu and is_gpu_available() and GPU_ENCODING_AVAILABLE
    
    # 构建基本命令
    ffmpeg_command = [
        FFMPEG_PATH,
        '-i', input_file,
        '-b:v', f'{target_bitrate}k',
    ]

    # 调整帧率
    if frame_rate and original_frame_rate > frame_rate:
        ffmpeg_command.extend(['-r', str(frame_rate)])

    # 添加编码器选项
    if gpu_enabled:
        print(f"使用GPU (NVENC) 编码: {input_file}")
        ffmpeg_command.extend(['-vcodec', 'h264_nvenc'])
    else:
        print(f"使用CPU (libx264) 编码: {input_file}")
        ffmpeg_command.extend(['-vcodec', 'libx264'])
        # 如果使用CPU编码，设置CPU线程数
        cpu_count = psutil.cpu_count()
        cpu_threads = max(1, int(cpu_count * max_usage))
        ffmpeg_command.extend(['-threads', str(cpu_threads)])
    
    ffmpeg_command.append(output_file)

    try:
        print(f"开始压缩视频: {input_file}")
        subprocess.run(ffmpeg_command, check=True, timeout=7200)  # 设置超时为2小时
        print(f"视频压缩成功：{output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"压缩视频时出错 {input_file}: {e}")
        return False
    except subprocess.TimeoutExpired:
        print(f"压缩视频超时 {input_file}，可能视频太大或编码太慢")
        return False
    except Exception as e:
        print(f"压缩视频异常 {input_file}: {e}")
        return False

def is_video_file(filename):
    """检查文件是否为视频文件"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp']
    _, ext = os.path.splitext(filename)
    return ext.lower() in video_extensions

def process_videos(directory, compression_ratio=0.5, frame_rate=None, use_gpu=False, max_usage=0.8):
    """处理指定目录中的所有视频文件，一旦有失败立即停止所有处理"""
    # 检查GPU编码支持
    if use_gpu and not GPU_ENCODING_AVAILABLE:
        print("警告: GPU编码不可用，自动降级到CPU编码")
        use_gpu = False
    
    # 收集所有视频文件
    video_files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and is_video_file(filename) and not filename.endswith('_Compressed.mp4'):
            video_files.append(filepath)
    
    if not video_files:
        print("当前目录未找到可处理的视频文件")
        return
    
    total_files = len(video_files)
    print(f"找到 {total_files} 个视频文件需要处理")
    
    # 尝试处理第一个视频文件
    filename = os.path.basename(video_files[0])
    print(f"\n正在处理视频: {filename}")
    
    success = compress_video(video_files[0], compression_ratio, frame_rate, use_gpu, max_usage)
    
    if not success:
        print("\n视频压缩失败，停止所有后续处理！")
        print("请解决问题后再尝试。可能的原因包括:")
        print("- NVIDIA驱动版本过低(需要551.76或更新)")
        print("- 视频格式不支持")
        print("- 磁盘空间不足")
        print("- FFmpeg配置问题")
        return
        
    print(f"\n处理完成: {filename} 压缩成功!")
    print("您可以继续处理更多视频文件，或修改脚本以批量处理。")

if __name__ == "__main__":
    try:
        # 检查ffmpeg是否存在
        if not os.path.exists(FFMPEG_PATH):
            print(f"错误: ffmpeg 未找到，请检查路径: {FFMPEG_PATH}")
            sys.exit(1)
            
        # 测试GPU编码功能
        GPU_ENCODING_AVAILABLE = test_gpu_encoding() if is_gpu_available() else False
            
        # 设置参数
        directory = "."  # 当前目录，根据需要修改
        compression_ratio = 0.1  # 压缩比例
        frame_rate = 30  # 目标帧率
        use_gpu = True  # 如果GPU可用，则使用GPU
        max_usage = 0.6  # CPU或GPU的最大使用率
        
        # 开始处理视频
        process_videos(directory, compression_ratio, frame_rate, use_gpu, max_usage)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序出现未预期的错误: {e}")
        sys.exit(1)