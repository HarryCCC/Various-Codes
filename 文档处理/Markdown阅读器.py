import tkinter as tk
from tkinter import scrolledtext
import markdown
from tkinterweb import HtmlFrame

def convert_markdown():
    markdown_text = input_text.get("1.0", tk.END)
    html_text = markdown.markdown(markdown_text, extensions=['markdown_katex'])
    html_text = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.css">
        <script src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/katex.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/katex@0.11.1/dist/contrib/auto-render.min.js"></script>
        <script>
            document.addEventListener("DOMContentLoaded", function() {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{left: "$$", right: "$$", display: true}},
                        {{left: "$", right: "$", display: false}},
                        {{left: "\\[", right: "\\]", display: true}},
                        {{left: "\\(", right: "\\)", display: false}}
                    ]
                }});
            }});
        </script>
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """
    output_frame.load_html(html_text)

# 创建主窗口
root = tk.Tk()
root.title("Markdown 转换器")
root.geometry("800x600")

# 使用grid布局管理器
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)

# 创建输入框
input_label = tk.Label(root, text="输入Markdown文本:")
input_label.grid(row=0, column=0, sticky='nw', padx=10, pady=5)

input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
input_text.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

# 创建显示框
output_label = tk.Label(root, text="转换后的HTML文本:")
output_label.grid(row=0, column=1, sticky='nw', padx=5, pady=5)

output_frame = HtmlFrame(root, horizontal_scrollbar="auto")
output_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

# 创建转换按钮
convert_button = tk.Button(root, text="转换", command=convert_markdown)
convert_button.grid(row=1, column=0, sticky='sw', padx=10, pady=10)

# 运行主循环
root.mainloop()
