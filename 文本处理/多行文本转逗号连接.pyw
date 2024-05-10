import tkinter as tk
from tkinter import scrolledtext

def convert_text():
    input_text = input_text_area.get("1.0", tk.END).strip()
    formatted_text = ','.join(line.strip() for line in input_text.split('\n') if line.strip())
    output_text_area.delete("1.0", tk.END)
    output_text_area.insert("1.0", formatted_text)

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text_area.get("1.0", tk.END))
    root.update()  # 现在剪贴板中有了text

root = tk.Tk()
root.title("Text Formatter")

input_text_area = scrolledtext.ScrolledText(root, height=10, width=40)
input_text_area.grid(row=0, column=0, padx=10, pady=10)

convert_button = tk.Button(root, text="CONVERT", command=convert_text)
convert_button.grid(row=1, column=0, padx=10, pady=10)

output_text_area = scrolledtext.ScrolledText(root, height=10, width=40)
output_text_area.grid(row=0, column=1, padx=10, pady=10)

copy_button = tk.Button(root, text="COPY", command=copy_to_clipboard)
copy_button.grid(row=1, column=1, padx=10, pady=10)

root.mainloop()
