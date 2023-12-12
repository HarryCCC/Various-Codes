import pandas as pd

# 读取同路径下的"midi_data.csv"文件，这里使用相对路径
df = pd.read_csv("midi_data.csv", encoding="ISO-8859-1")

# 删除列
df = df.drop('filename', axis=1)
df = df.drop('instrument', axis=1)

# 定义清洗函数
def clean_data(df):
    # 删除offset列中含有非数字的行
    df = df[~df['offset'].astype(str).str.contains('[^0-9./]')]

    # 删除duration列中含有非数字的行
    df = df[~df['duration'].astype(str).str.contains('[^0-9./]')]

    # 将offset和duration列中的数据转换为浮点数
    df['offset'] = pd.to_numeric(df['offset'], errors='coerce')
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

    # 删除在转换过程中变成NaN的行
    df = df.dropna(subset=['offset', 'duration'])

    # 删除任何存在空白格的一行
    df = df.dropna()

    return df

# 应用清洗数据的函数
cleaned_df = clean_data(df)

# 将清洗后的数据保存到当前目录下
cleaned_df.to_csv("cleaned_midi_data.csv", index=False)
