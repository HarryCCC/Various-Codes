import subprocess

def compress_video(input_path, output_path, bitrate='1000k', output_format='mp4'):
    """
    Compresses a video file to a specified bitrate and format, with progress displayed in the console.

    Args:
    input_path (str): Path to the input video file.
    output_path (str): Path where the output video file will be saved.
    bitrate (str): Target bitrate for compression (e.g., '1000k' for 1000 kbps).
    output_format (str): Output video format (e.g., 'mp4', 'avi').

    Returns:
    bool: True if compression is successful, False otherwise.
    """
    try:
        # Constructing the ffmpeg command for video compression
        command = [
            'ffmpeg',
            '-i', input_path,  # Input file
            '-b:v', bitrate,  # Video bitrate
            '-c:v', 'libx264',  # Video codec
            '-preset', 'fast',  # Preset for compression speed/efficiency tradeoff
            output_path + '.' + output_format  # Output file
        ]

        # Execute the command and handle progress
        process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
        for line in process.stderr:
            if "time=" in line:
                print(line.strip())
        
        process.wait()  # Wait for process to finish

        # Check if ffmpeg command was successful
        if process.returncode != 0:
            print("Video compression failed.")
            return False
        
        print("Video compressed successfully.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


success = compress_video('raw_camera.mp4', 'compressed_video', '1000k', 'mp4')

if success:
    print("Video compressed successfully.")
else:
    print("Video compression failed.")