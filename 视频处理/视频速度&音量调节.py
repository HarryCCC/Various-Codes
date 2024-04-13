import subprocess

def modify_video_speed_and_volume(input_path, output_path, speed_factor=1.0, volume_factor=1.0):
    """
    Modifies the speed and volume of a video file and displays progress.

    Args:
    input_path (str): Path to the input video file.
    output_path (str): Path where the modified video file will be saved.
    speed_factor (float): Factor to adjust the video speed (e.g., 0.5 for half speed, 2 for double speed).
    volume_factor (float): Factor to adjust the audio volume (e.g., 0.5 for half volume, 2 for double volume).

    Returns:
    bool: True if the operation is successful, False otherwise.
    """
    try:
        # Constructing the ffmpeg command for modifying video and audio
        command = [
            'ffmpeg',
            '-i', input_path,  # Input file
            '-filter_complex', f"[0:v]setpts={1/speed_factor}*PTS[v];[0:a]volume={volume_factor}[a]",  # Filters for video and audio
            '-map', '[v]', '-map', '[a]',  # Mapping the filtered video and audio
            '-c:v', 'libx264',  # Video codec
            '-preset', 'fast',  # Preset for the balance between compression speed and quality
            output_path  # Output file
        ]

        # Execute the command and handle progress
        process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            if "time=" in line:
                print(line.strip())
        
        process.wait()  # Wait for process to finish

        # Check if ffmpeg command was successful
        if process.returncode != 0:
            print("Failed to adjust video speed and volume.")
            return False
        
        print("Video speed and volume adjusted successfully.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


success = modify_video_speed_and_volume('raw_camera.mp4', 'modified_video.mp4', 1.4, 1.5)
if success:
    print("Video speed and volume adjusted successfully.")
else:
    print("Failed to adjust video speed and volume.")
