import PyPDF2
from PyPDF2 import PdfReader, PdfWriter, PageObject

def split_pdf(input_pdf, output_pdf, page_height, keep_center=False):
    # 打开输入的PDF文件
    with open(input_pdf, 'rb') as input_file:
        reader = PdfReader(input_file)
        writer = PdfWriter()
        
        num_pages = len(reader.pages)
        for i in range(num_pages):
            page = reader.pages[i]
            original_height = float(page.mediabox.top)
            original_width = float(page.mediabox.right)
            
            # 计算需要切割的段数
            num_splits = int(original_height // page_height) + 1
            
            for j in range(num_splits):
                # 计算每一段的上下边界
                lower_bound = max(original_height - (j + 1) * page_height, 0)
                upper_bound = original_height - j * page_height
                
                # 创建一个新的页面对象
                new_page = PageObject.create_blank_page(
                    width=original_width,
                    height=page_height
                )
                
                # 裁剪页面内容
                new_page.merge_page(page)
                
                if keep_center:
                    # 只保留中央60%的内容
                    center_width = original_width * 0.5
                    left_margin = (original_width - center_width) / 2
                    new_page.mediabox.lower_left = (left_margin, lower_bound)
                    new_page.mediabox.upper_right = (original_width - left_margin, upper_bound)
                else:
                    new_page.mediabox.lower_left = (0, lower_bound)
                    new_page.mediabox.upper_right = (original_width, upper_bound)
                
                # 将页面内容放缩到页面宽度一致
                new_page.scale_by(float(new_page.mediabox.right) / float(new_page.mediabox.width))
                
                writer.add_page(new_page)
        
        # 将新的页面写入输出的PDF文件
        with open(output_pdf, 'wb') as output_file:
            writer.write(output_file)

# 使用示例
input_pdf = 'input.pdf'
output_pdf = 'output.pdf'
page_height = 1811  # 自定义页面高度

# 调用函数，keep_center参数设置为True，只保留每页中央60%的内容并放缩
split_pdf(input_pdf, output_pdf, page_height, keep_center=True)
