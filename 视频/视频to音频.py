import ffmpeg

def convert_mp4_to_mp3_ffmpeg(video_path, audio_path):
    """
    Convert an MP4 video file to an MP3 audio file using ffmpeg.
    
    Args:
    video_path (str): The file path of the MP4 video.
    audio_path (str): The destination file path for the MP3 audio.
    """
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, format='mp3')
        .run()
    )

# 使用函数
convert_mp4_to_mp3_ffmpeg("video.mp4", "sound.mp3")
