import os
from googletrans import Translator

translator = Translator()

def translate_to_chinese(text):
    # 翻译文本为中文
    try:
        translation = translator.translate(text, dest='zh-cn')
        return translation.text
    except Exception as e:
        print(f"Error translating {text}: {str(e)}")
        return text  # 返回原文本以避免丢失信息

def rename_files(directory_path):
    files = [f for f in os.listdir(directory_path) if f.endswith('.mp3')]
    for file in files:
        filename_without_extension = os.path.splitext(file)[0]
        chinese_name = translate_to_chinese(filename_without_extension)
        new_filename = chinese_name.strip() + '.mp3'
        old_path = os.path.join(directory_path, file)
        new_path = os.path.join(directory_path, new_filename)
        os.rename(old_path, new_path)
        print(f'Renamed "{file}" to "{new_filename}"')

# 使用函数
rename_files('Musics')
