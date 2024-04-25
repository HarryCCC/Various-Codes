import csv
from music21 import converter, note, chord, instrument

def midi_to_csv(midi_file, csv_file):
    # 加载MIDI文件
    midi = converter.parse(midi_file)

    # 打开CSV文件进行写入
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['note/chord', 'offset', 'duration', 'velocity'])

        parts = instrument.partitionByInstrument(midi)
        if parts:  # 如果有多个音轨，遍历每个音轨
            for part in parts:
                for element in part.recurse():
                    if isinstance(element, note.Note):
                        writer.writerow([element.pitch, element.offset, element.duration.quarterLength, element.volume.velocity])
                    elif isinstance(element, chord.Chord):
                        writer.writerow(['.'.join(str(n) for n in element.normalOrder), element.offset, element.duration.quarterLength, element.volume.velocity])
        else:  # 如果没有音轨，则直接遍历midi的notes
            for element in midi.flat.notes:
                if isinstance(element, note.Note):
                    writer.writerow([element.pitch, element.offset, element.duration.quarterLength, element.volume.velocity])
                elif isinstance(element, chord.Chord):
                    writer.writerow(['.'.join(str(n) for n in element.normalOrder), element.offset, element.duration.quarterLength, element.volume.velocity])

midi_file = 'generated_music.mid'  # 您的MIDI文件路径
csv_file = 'generated_music.csv'  # 您想要创建的CSV文件路径
midi_to_csv(midi_file, csv_file)
