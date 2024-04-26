from pydub import AudioSegment
from pydub.playback import play

def modify_audio(file_path, output_path, volume_change_dB, speed_factor):
    """
    Modify an audio file's volume and speed.
    
    Args:
    file_path (str): The file path of the original audio file.
    output_path (str): The file path to save the modified audio file.
    volume_change_dB (float): Volume change in decibels (dB).
    speed_factor (float): Factor to change the speed (1.0 = original speed, <1 = slower, >1 = faster).
    """
    # Load the audio file
    sound = AudioSegment.from_mp3(file_path)
    
    # Adjust volume
    adjusted_sound = sound + volume_change_dB
    
    # Change speed
    new_frame_rate = int(sound.frame_rate * speed_factor)
    changed_speed_sound = adjusted_sound._spawn(adjusted_sound.raw_data, overrides={'frame_rate': new_frame_rate})
    
    # Export the modified sound
    changed_speed_sound.export(output_path, format="mp3")

# 使用函数
modify_audio("sound.mp3", "sound_modified.mp3", volume_change_dB=+10, speed_factor=1.25) # speed_factor>1 代表加速比率
