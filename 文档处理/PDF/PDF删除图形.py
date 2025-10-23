import fitz  # PyMuPDF

def remove_images_from_pdf(input_pdf_path, output_pdf_path):
    # 打开PDF文档
    pdf_document = fitz.open(input_pdf_path)
    
    # 遍历每一页
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # 获取页面上的所有图片信息
        image_list = page.get_images(full=True)
        
        # 遍历所有图片并删除
        for img in image_list:
            xref = img[0]
            page.delete_image(xref)
        
    # 保存处理后的PDF
    pdf_document.save(output_pdf_path)

# 使用示例
input_pdf_path = 'input.pdf'  # 输入PDF文件路径
output_pdf_path = 'output.pdf'  # 输出PDF文件路径
remove_images_from_pdf(input_pdf_path, output_pdf_path)
