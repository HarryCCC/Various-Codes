from moviepy.editor import VideoFileClip
from moviepy.video.fx.speedx import speedx

def change_video_speed(input_path, output_path, expected_seconds):
    # 加载视频文件
    clip = VideoFileClip(input_path)
    
    # 获取原始视频的时长
    original_duration = clip.duration
    
    # 计算需要的速度变化比率
    speed_change_factor = original_duration / expected_seconds
    
    # 应用速度变化
    modified_clip = speedx(clip, factor=speed_change_factor)
    
    # 输出变速后的视频文件
    modified_clip.write_videofile(output_path, codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

# 调用函数
input_video_path = 'final_video_with_subtitles.mp4'
output_video_path = 'output_final_video.mp4'
expected_duration = 120  # 假设我们希望视频长度为120秒

change_video_speed(input_video_path, output_video_path, expected_duration)
