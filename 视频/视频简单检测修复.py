import os
import subprocess
import re
import math

def get_video_duration(input_file):
    """
    获取视频时长（秒）。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    out, err = process.communicate()
    process.wait()
    duration_str = out.strip()
    if duration_str:
        try:
            return float(duration_str)
        except ValueError:
            return 0.0
    return 0.0

def get_video_avg_frame_rate(input_file):
    """
    获取平均帧率（返回一个浮点数）。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=avg_frame_rate",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    out, err = process.communicate()
    process.wait()
    fr_str = out.strip()
    if not fr_str:
        return 0.0

    # ffprobe 可能返回形如 "25/1" 或 "30000/1001" 这样的分数，需要转换成浮点数
    if '/' in fr_str:
        num, den = fr_str.split('/')
        if den == '0':  # 避免分母为 0
            return 0.0
        try:
            return float(num) / float(den)
        except ValueError:
            return 0.0
    else:
        try:
            return float(fr_str)
        except ValueError:
            return 0.0

def get_total_frames(input_file):
    """
    优先用 nb_frames 获取总帧数，若获取失败则尝试时长 x 帧率的方式。
    获取不到则返回 0，以便后续逻辑决定如何处理。
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_frames",
        "-of", "default=nokey=1:noprint_wrappers=1",
        input_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    out, err = process.communicate()
    process.wait()
    
    nb_frames = out.strip()
    if nb_frames.isdigit():
        return int(nb_frames)
    else:
        # 如果 nb_frames 拿不到，则尝试用时长 * 帧率估算一个总帧数
        duration = get_video_duration(input_file)
        avg_fps = get_video_avg_frame_rate(input_file)
        if duration > 0 and avg_fps > 0:
            return int(math.floor(duration * avg_fps))
        else:
            # 如果连时长或帧率都获取不到，只能返回 0，后续代码可决定如何处理
            return 0

def try_repair_with_copy(input_file, output_file):
    """
    使用“直接复制（不重新编码）”的方式进行修复，并显示进度（若能获取到总帧数）。
    """
    total_frames = get_total_frames(input_file)

    cmd = [
        "ffmpeg", "-y",
        "-err_detect", "ignore_err",
        "-i", input_file,
        "-c", "copy",
        "-movflags", "+faststart",
        output_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

    if total_frames > 0:
        # 若能获取到总帧数，则尝试根据 FFmpeg 的输出来显示进度
        for line in process.stderr:
            match = re.search(r'frame=\s*(\d+)', line)
            if match:
                frame_number = int(match.group(1))
                progress = (frame_number / total_frames) * 100
                print(f"进度: {progress:.2f}%", end='\r')
    else:
        # 如果无法获取到总帧数，直接输出 FFmpeg 日志（或者你可改成不输出）
        for line in process.stderr:
            print(line, end='')

    process.wait()
    return process.returncode

def try_repair_with_reencode(input_file, output_file):
    """
    使用“重新编码”方式修复视频，并显示进度（若能获取到总帧数）。
    """
    total_frames = get_total_frames(input_file)

    cmd = [
        "ffmpeg", "-y",
        "-err_detect", "ignore_err",
        "-i", input_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

    if total_frames > 0:
        for line in process.stderr:
            match = re.search(r'frame=\s*(\d+)', line)
            if match:
                frame_number = int(match.group(1))
                progress = (frame_number / total_frames) * 100
                print(f"进度: {progress:.2f}%", end='\r')
    else:
        for line in process.stderr:
            print(line, end='')

    process.wait()
    return process.returncode

def repair_video(video_path):
    """
    自动检测并尝试最大可能的方式进行修复。
    1) 不重新编码的复制封装。
    2) 若失败，进行重新编码。
    """
    base_name, ext = os.path.splitext(video_path)
    fixed_file = f"{base_name}_fixed{ext}"

    print(f"===> 正在尝试不重新编码修复：{video_path} -> {fixed_file}")
    result_copy = try_repair_with_copy(video_path, fixed_file)
    if result_copy == 0:
        print(f"\n[成功] 使用不重新编码方式已生成修复文件：{fixed_file}")
        return
    else:
        print("\n[失败] 不重新编码修复无法完成，转而尝试重新编码方式...")

    print(f"===> 正在尝试重新编码修复：{video_path} -> {fixed_file}")
    result_reencode = try_repair_with_reencode(video_path, fixed_file)
    if result_reencode == 0:
        print(f"\n[成功] 使用重新编码方式已生成修复文件：{fixed_file}")
        return
    else:
        print("\n[失败] 重新编码修复失败。")

    print("\n[提示] 若上述方法均失败，说明该视频文件损坏较严重。")
    print("可尝试：")
    print("  1) 使用专业修复工具（如 untrunc，需提供相同编解码参数的正常文件参考）。")
    print("  2) 更换输出格式（如 MKV）继续尝试。")
    print("  3) 寻找更完整的源文件或使用数据恢复工具。")

if __name__ == "__main__":
    video_file = "video.MP4"
    if not os.path.exists(video_file):
        print(f"文件 {video_file} 不存在，请确认已放置在当前目录。")
    else:
        repair_video(video_file)
