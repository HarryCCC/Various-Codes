from moviepy.editor import VideoFileClip

# 加载视频文件
clip = VideoFileClip("日出,海,海洋,波浪,海滩,兰萨罗特,西班牙,加那利群岛,早晨,早期的,太阳,夏天,美丽的,平静的.mp4")

# 调整视频尺寸
resized_clip = clip.resize(newsize=(1920, 1080))

# 输出调整后的视频，并尝试使用GPU加速
resized_clip.write_videofile("video_resized.mp4", codec='h264_nvenc')
