import os
import subprocess
import shutil
import time

def fix_mp4():
    print("=== 开始修复视频 ===")
    
    # === 固定的文件路径 ===
    # 输入输出文件路径
    input_file = "video.mp4"  # 当前目录下的video.mp4
    output_file = "video_fixed.mp4"  # 成功后输出的文件
    
    # 临时目录
    temp_dir = "temp_repair"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 临时文件
    temp_method1 = os.path.join(temp_dir, "method1.mp4")
    temp_method2_video = os.path.join(temp_dir, "video_only.mp4")
    temp_method2_audio = os.path.join(temp_dir, "audio_only.aac")
    temp_method3 = os.path.join(temp_dir, "method3.mp4")
    temp_method4 = os.path.join(temp_dir, "method4.mp4")
    
    # 检查输入文件
    if not os.path.exists(input_file):
        print(f"错误: 当前目录下未找到文件 '{input_file}'")
        return False
    
    # === 开始尝试修复 ===
    print(f"正在修复文件: {input_file}")
    fixed = False
    
    # 方法1: 简单流复制
    print("\n尝试方法1: 简单流复制...")
    try:
        result = subprocess.run([
            'ffmpeg', '-v', 'error', 
            '-i', input_file,
            '-c', 'copy', 
            '-y', temp_method1
        ], capture_output=True, text=True)
        
        # 验证
        if result.returncode == 0:
            validate = subprocess.run([
                'ffmpeg', '-v', 'error',
                '-i', temp_method1,
                '-f', 'null', '-'
            ], capture_output=True, text=True)
            
            if validate.returncode == 0:
                shutil.copy(temp_method1, output_file)
                print("方法1修复成功!")
                fixed = True
    except Exception as e:
        print(f"方法1失败: {str(e)}")
    
    # 如果方法1失败，尝试方法2
    if not fixed:
        print("\n尝试方法2: 分离并重建音视频流...")
        try:
            # 提取视频流
            subprocess.run([
                'ffmpeg', '-v', 'error',
                '-i', input_file,
                '-an', '-c:v', 'copy',
                '-y', temp_method2_video
            ], check=False, capture_output=True)
            
            # 提取音频流
            subprocess.run([
                'ffmpeg', '-v', 'error',
                '-i', input_file, 
                '-vn', '-c:a', 'copy',
                '-y', temp_method2_audio
            ], check=False, capture_output=True)
            
            # 检查是否提取成功
            has_video = os.path.exists(temp_method2_video) and os.path.getsize(temp_method2_video) > 0
            has_audio = os.path.exists(temp_method2_audio) and os.path.getsize(temp_method2_audio) > 0
            
            if has_video:  # 有视频流
                if has_audio:  # 有音频流
                    # 合并音视频
                    result = subprocess.run([
                        'ffmpeg', '-v', 'error',
                        '-i', temp_method2_video,
                        '-i', temp_method2_audio,
                        '-c', 'copy',
                        '-y', output_file
                    ], capture_output=True, text=True)
                else:  # 只有视频
                    shutil.copy(temp_method2_video, output_file)
                    result = subprocess.CompletedProcess(args=[], returncode=0)
                
                # 验证
                if result.returncode == 0:
                    validate = subprocess.run([
                        'ffmpeg', '-v', 'error',
                        '-i', output_file,
                        '-f', 'null', '-'
                    ], capture_output=True, text=True)
                    
                    if validate.returncode == 0:
                        print("方法2修复成功!")
                        fixed = True
        except Exception as e:
            print(f"方法2失败: {str(e)}")
    
    # 如果方法2失败，尝试方法4 (faststart)
    if not fixed:
        print("\n尝试方法4: 修复moov atom...")
        try:
            result = subprocess.run([
                'ffmpeg', '-v', 'error',
                '-i', input_file,
                '-c', 'copy',
                '-movflags', 'faststart',
                '-y', temp_method4
            ], capture_output=True, text=True)
            
            # 验证
            if result.returncode == 0:
                validate = subprocess.run([
                    'ffmpeg', '-v', 'error',
                    '-i', temp_method4,
                    '-f', 'null', '-'
                ], capture_output=True, text=True)
                
                if validate.returncode == 0:
                    shutil.copy(temp_method4, output_file)
                    print("方法4修复成功!")
                    fixed = True
        except Exception as e:
            print(f"方法4失败: {str(e)}")
    
    # 如果方法4失败，最后尝试方法3 (重编码)
    if not fixed:
        print("\n尝试方法3: 重新编码 (最终尝试)...")
        try:
            result = subprocess.run([
                'ffmpeg', '-v', 'error',
                '-err_detect', 'ignore_err',
                '-i', input_file,
                '-c:v', 'libx264', '-crf', '23',
                '-c:a', 'aac', '-q:a', '100',
                '-y', temp_method3
            ], capture_output=True, text=True)
            
            # 验证
            if result.returncode == 0:
                validate = subprocess.run([
                    'ffmpeg', '-v', 'error',
                    '-i', temp_method3,
                    '-f', 'null', '-'
                ], capture_output=True, text=True)
                
                if validate.returncode == 0:
                    shutil.copy(temp_method3, output_file)
                    print("方法3修复成功!")
                    fixed = True
        except Exception as e:
            print(f"方法3失败: {str(e)}")
    
    # 清理临时文件
    try:
        shutil.rmtree(temp_dir)
        print("临时文件已清理")
    except:
        pass
    
    # 输出结果
    if fixed:
        print("\n===================================")
        print("修复成功!")
        print(f"修复后的文件: {output_file}")
        print("===================================")
        return True
    else:
        print("\n===================================")
        print("所有修复方法都失败!")
        print("视频文件可能已严重损坏，无法修复")
        print("===================================")
        
        # 如果修复失败，删除可能部分生成的输出文件
        if os.path.exists(output_file):
            os.remove(output_file)
            
        return False


if __name__ == "__main__":
    fix_mp4()