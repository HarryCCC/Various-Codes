# 定义一个函数，用来把文本分割成部分
def split_text(text):
    # 初始化一个空列表，用来存储分割后的部分
    parts = []
    # 初始化一个空字符串，用来存储当前的部分
    part = ""
    # 初始化一个计数器，用来记录当前部分的字符数
    count = 0
    # 把文本按照空格和换行符分割成单词列表
    words = text.split()
    # 遍历每个单词
    for word in words:



        # 如果当前部分已经达到或者接近了5000个字符（差距小于800），就把当前部分添加到列表中，并清空当前部分和计数器
        # 使用800时，本代码的实际效果可以将每个PART.txt的字符数调整在4950左右
        if abs(count + len(word) - 5000) < 800:
            parts.append(part)
            part = ""
            count = 0





        # 把这个单词添加到当前部分，并更新计数器
        part += word + " "
        count += len(word)
        # 如果当前部分已经达到了5000个字符，就在当前部分后面加上两个换行符，并清空计数器（保证每个部分都是5000个字符）
        if count == 5000:
            part += "\n\n"
            count = 0
    # 如果最后还有剩余的部分，也添加到列表中
    if part:
        parts.append(part)
    # 返回分割后的部分列表
    return parts

# 从桌面上的 txt 文件读取文本（文件名为 新建 Text Document.txt）
with open("C:\\Users\\11470\\Desktop\\新建 Text Document.txt", "r", encoding="utf-8") as f:
    text = f.read()
# 消除掉输入文本中不必要的换行（以空格替代）
text = text.replace("\n", " ")
# 调用函数，得到分割后的部分列表
parts = split_text(text)
# 打印每个部分（可以保存到文件或其他地方）
for i, part in enumerate(parts):
    print(f"第{i+1}个部分：")
    print(part)
    
# 输出到桌面，把每个部分导出为 txt 文件（文件名为 part_序号.txt）
for i, part in enumerate(parts):
    with open(f"C:\\Users\\11470\\Desktop\\part_{i+1}.txt", "w", encoding="utf-8") as f:
        f.write(part)


