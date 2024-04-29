import tkinter as tk
from tkinter import scrolledtext
import threading

def convert_text():
    # 获取输入框中的文本，并去除首尾空格
    input_text = input_text_area.get("1.0", tk.END).strip()
    # 计算替换次数
    count = input_text.count('(') + input_text.count(')') + input_text.count('（') + input_text.count('）')
    # 替换小括号为大括号
    formatted_text = input_text.replace('(', '{').replace(')', '}')
    formatted_text = formatted_text.replace('（', '{').replace('）', '}')
    # 清空输出框，并将格式化后的文本放入输出框
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", formatted_text)
    # 更新状态标签显示替换数量并设置自动清除
    status_label.config(text=f"共修改了{count}处小括号")
    threading.Timer(3, lambda: status_label.config(text="")).start()

def copy_to_clipboard():
    # 清空剪贴板并将输出框中的文本复制到剪贴板
    root.clipboard_clear()
    root.clipboard_append(output_text_area.get("1.0", tk.END))
    root.update()  # 更新剪贴板内容
    # 显示复制成功信息并设置自动清除
    copy_status_label.config(text="复制成功！")
    threading.Timer(2, lambda: copy_status_label.config(text="")).start()

# 创建主窗口
root = tk.Tk()
root.title("括号转换器")

# 创建并放置输入文本框
input_text_area = scrolledtext.ScrolledText(root, height=10, width=40)
input_text_area.grid(row=1, column=0, padx=10, pady=10)

# 创建并放置转换按钮
convert_button = tk.Button(root, text="转换", command=convert_text)
convert_button.grid(row=2, column=0, padx=10, pady=10)

# 创建并放置输出文本框
output_text_area = scrolledtext.ScrolledText(root, height=10, width=40)
output_text_area.grid(row=1, column=1, padx=10, pady=10)

# 创建并放置复制按钮
copy_button = tk.Button(root, text="复制", command=copy_to_clipboard)
copy_button.grid(row=2, column=1, padx=10, pady=10)

# 创建状态标签（用于显示替换计数）
status_label = tk.Label(root, text="", font=('Arial', 12))
status_label.grid(row=0, column=0, padx=10, pady=10)

# 创建复制状态标签（用于显示复制成功信息）
copy_status_label = tk.Label(root, text="", font=('Arial', 12))
copy_status_label.grid(row=0, column=1, padx=10, pady=10)

# 启动主事件循环
root.mainloop()
