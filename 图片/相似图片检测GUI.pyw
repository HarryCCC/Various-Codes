# -*- coding: utf-8 -*-

"""
相似图片可视化审查与删除工具
版本: 2.2 (GUI版)
功能:
- 新增“扫描当前目录”快捷按钮，一键扫描程序所在文件夹。
- 保留“扫描其他文件夹”功能。
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import threading
import imagehash
import sys
import subprocess

# --- 从之前脚本继承的核心逻辑 ---
# (compute_hashes and find_similar_images functions remain the same)
def compute_hashes(directory: str, progress_callback) -> dict:
    hashes = {}
    image_files = []
    supported_extensions = ('.webp', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic', '.heif')
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(supported_extensions):
                image_files.append(os.path.join(root, file))

    if not image_files: return {}
    
    for i, filepath in enumerate(image_files):
        try:
            with Image.open(filepath) as img:
                h = imagehash.phash(img)
                hashes[filepath] = h
            progress_callback(f"正在计算哈希: {i+1}/{len(image_files)}")
        except Exception:
            continue
    return hashes

def find_similar_images(hashes: dict, threshold: int, progress_callback) -> list:
    similar_groups, processed_files = [], set()
    filenames = list(hashes.keys())
    if not filenames: return []

    for i in range(len(filenames)):
        progress_callback(f"正在比较图片: {i+1}/{len(filenames)}")
        f1 = filenames[i]
        if f1 in processed_files: continue
        
        current_group = [f1]
        for j in range(i + 1, len(filenames)):
            f2 = filenames[j]
            if f2 in processed_files: continue
            if hashes[f1] - hashes[f2] <= threshold:
                current_group.append(f2)
        
        if len(current_group) > 1:
            similar_groups.append(current_group)
            for item in current_group:
                processed_files.add(item)
    return similar_groups

# --- 全新的GUI应用类 ---
class SimilarityReviewer:
    SIMILARITY_THRESHOLD = 5
    THUMBNAIL_HEIGHT = 300

    def __init__(self, root):
        self.root = root
        self.root.title("相似图片审查工具 v2.2")
        self.root.geometry("900x600")

        self.similar_groups = []
        self.current_group_index = -1
        self.selection_vars = {}

        self.setup_initial_ui()

    def setup_initial_ui(self):
        """设置初始用户界面"""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        tk.Label(self.main_frame, text="请选择扫描模式", font=("Arial", 14)).pack(pady=20)
        
        # --- UI 变更：按钮功能和文字调整 ---
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        # 新增“扫描当前目录”按钮
        tk.Button(button_frame, text="扫描当前目录", command=self.scan_current_directory, font=("Arial", 12), bg="#cceeff").pack(side='left', padx=10, ipady=5)
        
        # 保留并微调“扫描其他文件夹”按钮
        tk.Button(button_frame, text="扫描其他文件夹...", command=self.select_other_folder, font=("Arial", 12)).pack(side='left', padx=10, ipady=5)

        self.status_label = tk.Label(self.main_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=20)
    
    def get_script_directory(self):
        """获取脚本所在的目录，兼容打包情况"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def scan_current_directory(self):
        """扫描脚本所在的当前目录"""
        directory = self.get_script_directory()
        if directory:
            self.start_scan(directory)

    def select_other_folder(self):
        """选择其他目录进行扫描"""
        directory = filedialog.askdirectory()
        if directory:
            self.start_scan(directory)

    def start_scan(self, directory):
        self.main_frame.destroy()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both')

        self.status_label = tk.Label(self.main_frame, text=f"正在扫描: {directory}\n\n请稍候...", font=("Arial", 12))
        self.status_label.pack(pady=50)

        scan_thread = threading.Thread(target=self._scan_worker, args=(directory,))
        scan_thread.start()

    def _scan_worker(self, directory):
        hashes = compute_hashes(directory, self.update_status)
        self.similar_groups = find_similar_images(hashes, self.SIMILARITY_THRESHOLD, self.update_status)
        self.root.after(0, self.setup_review_ui)

    def update_status(self, message):
        self.status_label.config(text=message)

    def setup_review_ui(self):
        self.main_frame.destroy()
        if not self.similar_groups:
            messagebox.showinfo("扫描完成", "未找到任何相似的图片组。")
            self.setup_initial_ui()
            return
            
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill='x', padx=10, pady=5)
        self.nav_label = tk.Label(nav_frame, text="", font=("Arial", 12))
        self.nav_label.pack(side='left')

        tk.Button(nav_frame, text="下一组 →", command=self.next_group).pack(side='right')
        tk.Button(nav_frame, text="← 上一组", command=self.prev_group).pack(side='right', padx=5)

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(expand=True, fill='both')
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=canvas.xview)
        canvas.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(side='bottom', fill='x')
        canvas.pack(side='left', expand=True, fill='both')
        
        self.image_display_frame = tk.Frame(canvas)
        canvas.create_window((0,0), window=self.image_display_frame, anchor='nw')
        
        self.image_display_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        action_frame = tk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=10)
        tk.Button(action_frame, text="❌ 删除选中项", bg="#ff4d4d", fg="white", font=("Arial", 12, "bold"), command=self.delete_selected).pack(side='right')

        self.current_group_index = 0
        self.show_group()

    def show_group(self):
        for widget in self.image_display_frame.winfo_children():
            widget.destroy()
        self.selection_vars.clear()

        group = self.similar_groups[self.current_group_index]
        self.nav_label.config(text=f"第 {self.current_group_index + 1} / {len(self.similar_groups)} 组")

        for filepath in group:
            item_frame = tk.Frame(self.image_display_frame, padx=10, pady=10)
            item_frame.pack(side='left', anchor='n')

            try:
                with Image.open(filepath) as img:
                    img.thumbnail((self.THUMBNAIL_HEIGHT*2, self.THUMBNAIL_HEIGHT))
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label = tk.Label(item_frame, image=photo)
                    img_label.image = photo
                    img_label.pack()

                    var = tk.BooleanVar()
                    chk = tk.Checkbutton(item_frame, text=os.path.basename(filepath), variable=var, wraplength=self.THUMBNAIL_HEIGHT)
                    chk.pack()
                    self.selection_vars[filepath] = var
            except Exception as e:
                tk.Label(item_frame, text=f"无法加载\n{os.path.basename(filepath)}\n{e}", fg="red", wraplength=200).pack()

    def next_group(self):
        if self.current_group_index < len(self.similar_groups) - 1:
            self.current_group_index += 1
            self.show_group()

    def prev_group(self):
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.show_group()

    def delete_selected(self):
        to_delete = [fp for fp, var in self.selection_vars.items() if var.get()]
        if not to_delete:
            messagebox.showwarning("未选择", "您没有选择任何要删除的图片。")
            return

        confirm_msg = "您确定要永久删除以下文件吗？\n\n" + "\n".join([os.path.basename(f) for f in to_delete])
        if messagebox.askyesno("确认删除", confirm_msg):
            deleted_count = 0
            for filepath in to_delete:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    messagebox.showerror("删除失败", f"无法删除文件：{filepath}\n原因: {e}")
            
            messagebox.showinfo("操作完成", f"成功删除了 {deleted_count} 个文件。")
            
            current_group = self.similar_groups[self.current_group_index]
            self.similar_groups[self.current_group_index] = [f for f in current_group if f not in to_delete]
            
            if len(self.similar_groups[self.current_group_index]) < 2:
                self.similar_groups.pop(self.current_group_index)
                if self.current_group_index >= len(self.similar_groups) and self.similar_groups:
                    self.current_group_index = len(self.similar_groups) - 1
            
            if not self.similar_groups:
                self.setup_review_ui()
            else:
                self.show_group()


if __name__ == "__main__":
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
        
    root = tk.Tk()
    app = SimilarityReviewer(root)
    root.mainloop()