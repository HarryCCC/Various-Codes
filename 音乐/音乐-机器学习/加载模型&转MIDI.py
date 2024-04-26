import numpy as np
import joblib
from tensorflow.keras.models import load_model
from music21 import instrument, note, chord, stream

# === 可调整参数 ===
num_generated = 180  # 生成的音符数量
temperature = 1.2    # 用于采样的温度

# === 加载保存的模型和数据 ===
model = load_model('data/best_model.h5')
encoder = joblib.load('data/encoder.pkl')
onehot_encoder = joblib.load('data/onehot_encoder.pkl')
scaler = joblib.load('data/scaler.pkl')
sequence_length = np.load('data/sequence_length.npy').item()

def sample(preds, temperature=1.0):
    """对预测结果进行温度缩放并采样"""
    preds = np.asarray(preds).astype('float64')
    
    # 添加一个小的正值以避免 log(0) 的情况
    preds = np.clip(preds, 1e-10, 1 - 1e-10)

    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)

    # 确保概率分布的总和严格等于1
    preds = preds / np.sum(preds)

    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)



def generate_notes(model, sequence_length, num_notes_classes, num_generated=150, temperature=1.0):
    """使用模型生成新的音符序列"""
    initial_pattern = np.random.randint(0, num_notes_classes, size=(sequence_length, 1))
    initial_pattern = onehot_encoder.transform(initial_pattern).astype(np.float32)

    # 初始化其他特征
    initial_features = np.full((sequence_length, 3), 0.5)
    pattern = np.hstack([initial_pattern, initial_features])

    prediction_output = []

    # 生成音符
    for note_index in range(num_generated):
        prediction_input = np.reshape(pattern, (1, sequence_length, -1))
        prediction = model.predict(prediction_input, verbose=0)[0]

        note_pred = prediction[:num_notes_classes]
        note_index = sample(note_pred, temperature)
        result_note = encoder.inverse_transform([note_index])[0]

        # 处理其他特征
        feature_pred = prediction[-3:]
        features = scaler.inverse_transform([feature_pred])[0]

        prediction_output.append((result_note, *features))

        next_input = np.concatenate([onehot_encoder.transform([[note_index]]).astype(np.float32), [features]], axis=1)
        pattern = np.vstack([pattern[1:], next_input])

    return prediction_output


def create_midi(prediction_output, filename='generated_music.mid'):
    """将预测出的音符序列转换为MIDI文件"""
    current_offset = 0  # 当前音符的开始时间
    output_notes = []

    for pattern, relative_offset, duration, velocity in prediction_output:
        # 限制间隔时间，防止音符之间间隔过长
        relative_offset = min(relative_offset, 1.5)  # 假设最大间隔为1

        # 调整声音大小，确保其在合理的范围内
        velocity = min(max(int(velocity), 64), 127)

        current_offset += relative_offset  # 累加相对偏移量来得到绝对 offset

        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            chord_notes = []
            for current_note in notes_in_chord:
                new_note = note.Note(int(current_note))
                new_note.storedInstrument = instrument.Piano()
                new_note.volume.velocity = velocity
                chord_notes.append(new_note)
            new_chord = chord.Chord(chord_notes)
            new_chord.duration.quarterLength = duration
            new_chord.offset = current_offset
            output_notes.append(new_chord)
        else:
            new_note = note.Note(pattern)
            new_note.offset = current_offset
            new_note.duration.quarterLength = duration
            new_note.storedInstrument = instrument.Piano()
            new_note.volume.velocity = velocity
            output_notes.append(new_note)

    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp=filename)

num_notes_classes = onehot_encoder.transform([[0]]).shape[1]
generated_notes = generate_notes(model, sequence_length, num_notes_classes, num_generated, temperature)

create_midi(generated_notes, 'generated_music.mid')