# 导入reportlab模块
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# 注册中文字体
font_name = 'STSong-Light'
pdfmetrics.registerFont(UnicodeCIDFont(font_name))

# 创建一个PDF文档对象，指定页面大小和边距
pdf_file = r'C:\Users\11470\Desktop\example.pdf' # 使用input函数来获取用户的输入
pdf_doc = canvas.Canvas(pdf_file, pagesize=A4)
margin = 2 * cm

# 设置字体和字号
font_size = 36
pdf_doc.setFont(font_name, font_size)

# 循环十次，每次创建一个新的页面，并在页面中央绘制“这是一个范例”的文本
text = "这是一个范例"
for i in range(10):
    # 计算文本的宽度和高度
    text_width = pdf_doc.stringWidth(text, font_name, font_size)
    text_height = font_size * 1.2

    # 计算文本的位置，使其居中显示
    x = (A4[0] - text_width) / 2
    y = (A4[1] - text_height) / 2

    # 绘制文本
    pdf_doc.drawString(x, y, text)

    # 创建新的页面
    pdf_doc.showPage()

# 保存PDF文档，并关闭画布对象
pdf_doc.save()
