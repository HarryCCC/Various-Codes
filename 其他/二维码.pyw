import qrcode
from PIL import Image
import io

url = "http://www.baidu.com"

# Text to be encoded in the QR code
text = "你辛苦了宝贝，谢谢~\
    在QR码的布局中，数据模块、纠错码模块和时间同步图案是构成QR码的三个主要部分，它们各自有不同的功能和位置：\
数据模块：\
功能：数据模块用于存储实际的编码数据，如文本、数字或网址。\
位置：数据模块分布在QR码的整个码区内，除了定位图案和格式信息区域。\
纠错码模块：\
功能：纠错码模块包含用于检测和纠正错误的额外信息。这些信息是根据Reed-Solomon纠错算法生成的。\
位置：纠错码模块通常位于QR码的底部，它们与数据模块交错排列。\
时间同步图案（也称为“定位图案”）：\
功能：时间同步图案用于帮助扫描设备从任何方向快速定位QR码。这些图案确保扫描器可以识别QR码的旋转方向并正确解读数据。\
位置：在QR码的三个角落各有一个大的定位图案，每个图案由一个小的相同图案环绕。这些图案有助于扫描器确定QR码的边界和方向。\
除了这三个主要部分，QR码还包括：\
格式信息：包含纠错级别和掩码图案的信息，用于解码时正确解释数据。\
版本信息（仅当版本大于7时存在）：指示QR码的版本号，即大小和容量。\
这些部分共同工作，确保QR码可以被快速、准确地扫描和解读。"

# Combining the text and URL in a format that can be scanned by some QR code readers to display the text and redirect to the URL
combined_data = f"{url}\n{text}"

# Generate QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(combined_data)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="grey", back_color="white")

# Save the image to a buffer
buffer = io.BytesIO()
img.save(buffer, format="PNG")
buffer.seek(0)

# Display the QR code image
img.show()

# Provide the buffer for download
buffer.getvalue(), buffer.tell()
