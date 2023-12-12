import pypinyin
from pypinyin import lazy_pinyin


def sort_text_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines.sort(key=lambda x: lazy_pinyin(x)[0])
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line)

sort_text_file(r'C:\Users\11470\Desktop\123.txt', r'C:\Users\11470\Desktop\abc.txt')
