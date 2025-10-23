# 导入PyPDF2模块
import PyPDF2

# 打开输入的PDF文档，获取文档对象和总页数
input_file = r'C:\Users\11470\Desktop\123.pdf'
input_pdf = PyPDF2.PdfReader(input_file) # 使用PdfReader而不是PdfFileReader
total_pages = len(input_pdf.pages) # 使用input_pdf.pages而不是input_pdf.getNumPages()

# 创建一个空的字典，用于存储每一页的内容和出现次数
content_dict = {}

# 遍历每一页，将每一页的内容转换为字符串，并去除空白字符
for i in range(total_pages):
    page = input_pdf.pages[i] # 使用input_pdf.pages[i]而不是input_pdf.getPage(i)
    content = page.extract_text().strip()
    # 如果该页的内容在字典中不存在，就将其添加到字典中，并将出现次数设为1
    if content not in content_dict:
        content_dict[content] = [1, i]
    # 如果该页的内容在字典中已经存在，就将其出现次数加1
    else:
        content_dict[content][0] += 1

# 创建一个空的PDF文档对象，用于输出结果
output_pdf = PyPDF2.PdfWriter() # 使用PdfWriter而不是PdfFileWriter

# 再次遍历每一页，如果该页的内容在字典中的出现次数为1，或者该页是该内容第一次出现的位置，就将该页添加到输出文档中
for i in range(total_pages):
    page = input_pdf.pages[i]
    content = page.extract_text().strip()
    if content_dict[content][0] == 1 or content_dict[content][1] == i:
        output_pdf.add_page(page)

# 保存输出文档，并关闭输入和输出文档
output_file = r'C:\Users\11470\Desktop\abc.pdf'
with open(output_file, "wb") as f:
    output_pdf.write(f)

input_pdf.stream.close()
f.close()

print("完成！")
