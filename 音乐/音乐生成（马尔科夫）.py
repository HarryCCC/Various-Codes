# 导入music21库
from music21 import *
import random

# 定义一个马尔科夫链类
class MarkovChain:

    # 初始化方法，接受一个状态列表和一个转移矩阵
    def __init__(self, states, matrix):
        self.states = states # 状态列表
        self.matrix = matrix # 转移矩阵
        self.current_state = None # 当前状态

    # 选择一个初始状态的方法，根据状态列表中的概率随机选择
    def start(self):
        self.current_state = random.choices(self.states, weights=self.states)[0]
        return self.current_state

    # 转移到下一个状态的方法，根据转移矩阵中的概率随机选择
    def move(self):
        i = self.states.index(self.current_state) # 获取当前状态在状态列表中的索引
        self.current_state = random.choices(self.states, weights=self.matrix[i])[0] # 根据转移矩阵中对应行的概率随机选择下一个状态
        return self.current_state

# 定义一个音符序列生成器类
class NoteSeqGenerator:

    # 初始化方法，接受一个音阶对象和一个马尔科夫链对象
    def __init__(self, scale, markov_chain):
        self.scale = scale # 音阶对象
        self.markov_chain = markov_chain # 马尔科夫链对象

    # 生成音符序列的方法，接受一个长度参数
    def generate(self, length):
        notes = [] # 空列表，用来存储音符对象
        self.markov_chain.start() # 选择初始状态
        for _ in range(length): # 循环length次
            degree = self.markov_chain.current_state # 获取当前状态，即音阶中的度数
            note = self.scale.pitchFromDegree(degree) # 根据度数获取对应的音符对象
            notes.append(note) # 将音符对象添加到列表中
            self.markov_chain.move() # 转移到下一个状态
        return notes # 返回音符对象列表

# 创建一个音乐流对象
s = stream.Stream()

# 创建一个音阶对象，这里使用C小调（C-Eb-G）
scale = scale.MinorScale('C')

# 创建一个马尔科夫链对象，这里使用1-7七个度数作为状态，转移矩阵是随机生成的
states = [1, 2, 3, 4, 5, 6, 7] # 状态列表
matrix = [[random.random() for _ in range(7)] for _ in range(7)] # 转移矩阵，是一个7x7的二维列表，每个元素是一个0-1之间的随机数
markov_chain = MarkovChain(states, matrix) # 创建马尔科夫链对象

# 创建一个音符序列生成器对象，传入音阶对象和马尔科夫链对象
note_seq_generator = NoteSeqGenerator(scale, markov_chain)

# 生成一个长度为16的音符序列
notes = note_seq_generator.generate(16)

# 创建一个和弦序列，这里使用C小调中的六个次要和弦和一个转换和弦：Cm、Ddim、Eb、Fm、Gm、Ab、Bb7
chords = [chord.Chord(['C4', 'Eb4', 'G4']), # Cm和弦
          chord.Chord(['D4', 'F4', 'Ab4']), # Ddim和弦
          chord.Chord(['Eb4', 'G4', 'Bb4']), # Eb和弦
          chord.Chord(['F4', 'Ab4', 'C5']), # Fm和弦
          chord.Chord(['G4', 'Bb4', 'D5']), # Gm和弦
          chord.Chord(['Ab4', 'C5', 'Eb5']), # Ab和弦
          chord.Chord(['Bb4', 'D5', 'F5', 'Ab5'])] # Bb7和弦

# 创建一个时值列表
durations = [2, 1.75, 1.5, 1.25, 1, 0.75, 0.5]

# 将音符序列和和弦序列交替添加到音乐流中，每个音符和和弦的时值都是随机选择的
for i in range(16):
    n = note.Note(notes[i]) # 创建音符对象，使用note.Note()函数
    n.duration.quarterLength = random.choice(durations) # 随机选择一个时值，赋值给音符对象的duration属性
    s.append(n) # 添加音符
    
    # 根据i的余数，创建不同的和弦对象
    if i % 7 == 0:
        c = chord.Chord(['C4', 'Eb4', 'G4']) # Cm和弦
    elif i % 7 == 1:
        c = chord.Chord(['D4', 'F4', 'Ab4']) # Ddim和弦
    elif i % 7 == 2:
        c = chord.Chord(['Eb4', 'G4', 'Bb4']) # Eb和弦
    elif i % 7 == 3:
        c = chord.Chord(['F4', 'Ab4', 'C5']) # Fm和弦
    elif i % 7 == 4:
        c = chord.Chord(['G4', 'Bb4', 'D5']) # Gm和弦
    elif i % 7 == 5:
        c = chord.Chord(['Ab4', 'C5', 'Eb5']) # Ab和弦
    elif i % 7 == 6:
        c = chord.Chord(['Bb4', 'D5', 'F5', 'Ab5']) # Bb7和弦
    else:
        c = chord.Chord(['G4', 'Bb4', 'D5', 'F5']) # Gm7和弦
    
    c.duration.quarterLength = random.choice(durations) # 随机选择一个时值，赋值给和弦对象的duration属性
    s.append(c) # 添加和弦

# 播放音乐流
s.show('midi')
