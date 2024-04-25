import csv
import os
import re
import time
from music21 import converter, note, chord, instrument, tempo, stream

def natural_sort_key(s):
    """ 自然排序辅助函数 """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

midi_folder = 'MIDI'
csv_filename = 'midi_data.csv'
csv_header = ['filename', 'instrument', 'note/chord', 'offset', 'duration', 'velocity']
max_process_time = 30  # 最大处理时间（秒）

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_header)
    
    counter = 0
    
    # 获取MIDI文件列表并进行自然排序
    midi_files = sorted(filter(lambda f: f.endswith(('.mid', '.midi')), os.listdir(midi_folder)), key=natural_sort_key)

    for midi_file in midi_files:
        start_time = time.time()  # 开始处理文件的时间
        try:
            file_path = os.path.join(midi_folder, midi_file)
            midi = converter.parse(file_path)
            parts = instrument.partitionByInstrument(midi)
            
            if parts:
                for part in parts:
                    inst = part.getInstrument()
                    current_instrument = inst.instrumentName if inst else 'Unknown'
                    for element in part.recurse():
                        if time.time() - start_time > max_process_time:
                            raise TimeoutError("Processing time exceeded the limit")
                        if isinstance(element, note.Note):
                            writer.writerow([midi_file, current_instrument, element.pitch, element.offset, element.duration.quarterLength, element.volume.velocity])
                        elif isinstance(element, chord.Chord):
                            writer.writerow([midi_file, current_instrument, '.'.join(str(n) for n in element.normalOrder), element.offset, element.duration.quarterLength, element.volume.velocity])
            else:
                for element in midi.flat.notes:
                    if time.time() - start_time > max_process_time:
                        raise TimeoutError("Processing time exceeded the limit")
                    if isinstance(element, note.Note):
                        writer.writerow([midi_file, None, 'Piano', element.pitch, element.offset, element.duration.quarterLength, element.volume.velocity])
                    elif isinstance(element, chord.Chord):
                        writer.writerow([midi_file, None, 'Piano', '.'.join(str(n) for n in element.normalOrder), element.offset, element.duration.quarterLength, element.volume.velocity])
            
            counter += 1
            print(f'Processed {counter} MIDI files: {midi_file}')
        except TimeoutError as e:
            print(f'Skipping {midi_file} due to time limit: {e}')
        except Exception as e:
            print(f'Error processing {midi_file}: {e}')

print(f'Total {counter} MIDI files processed.')
