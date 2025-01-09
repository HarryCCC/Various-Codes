import os
import subprocess
import re

def get_total_frames(input_file):
    """
    使用ffprobe获取视频文件的总帧数。
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=nb_frames",
        "-of", "default=nokey=1:noprint_wrappers=1",
        input_file
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    total_frames = process.stdout.read().strip()
    process.wait()
    return int(total_frames)

def try_repair_with_copy(input_file, output_file):
    """
    使用“直接复制（不重新编码）”的方式进行修复，并显示进度。
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
    
    for line in process.stderr:
        match = re.search(r'frame=\s*(\d+)', line)
        if match:
            frame_number = int(match.group(1))
            progress = (frame_number / total_frames) * 100
            print(f"进度: {progress:.2f}%", end='\r')
    
    process.wait()
    
    return process.returncode

def try_repair_with_reencode(input_file, output_file):
    """
    使用“重新编码”方式修复视频，并显示进度。
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
    
    for line in process.stderr:
        match = re.search(r'frame=\s*(\d+)', line)
        if match:
            frame_number = int(match.group(1))
            progress = (frame_number / total_frames) * 100
            print(f"进度: {progress:.2f}%", end='\r')
    
    process.wait()
    
    return process.returncode

def repair_video(video_path):
    """
    自动检测并尝试最大可能的方式进行修复。
    1) 不重新编码的复制封装。
    2) 重新编码。
    """
    base_name, ext = os.path.splitext(video_path)
    fixed_file = f"{base_name}_fixed{ext}"
    
    print(f"===> 正在尝试不重新编码修复：{video_path} -> {fixed_file}")
    result_copy = try_repair_with_copy(video_path, fixed_file)
    if result_copy == 0:
        print(f"[成功] 使用不重新编码方式已生成修复文件：{fixed_file}")
        return
    else:
        print("[失败] 不重新编码修复无法完成，转而尝试重新编码方式...")

    print(f"===> 正在尝试重新编码修复：{video_path} -> {fixed_file}")
    result_reencode = try_repair_with_reencode(video_path, fixed_file)
    if result_reencode == 0:
        print(f"[成功] 使用重新编码方式已生成修复文件：{fixed_file}")
        return
    else:
        print("[失败] 重新编码修复失败。")

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