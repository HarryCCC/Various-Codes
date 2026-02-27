import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import tkinter.font as tkfont
from pathlib import Path
import string
import platform

# -----------------------------------------------------------------------------
# 依赖检查与导入：尝试导入 tkinterdnd2 以支持拖拽
# -----------------------------------------------------------------------------
HAS_DND = False
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    # 如果没有安装库，定义一个伪类以防报错，并在运行时提示用户
    class TkinterDnD:
        class Tk(tk.Tk): pass
    DND_FILES = None

# =============================================================================
#  自定义多选文件夹选择器 (保持原版逻辑不变)
# =============================================================================
class MultiFolderSelector(tk.Toplevel):
    """
    一个美观的、支持多选的文件夹浏览弹窗。
    集成“快速访问”功能。
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("批量添加文件夹 (按住 Ctrl 或 Shift 多选)")
        self.geometry("700x600")
        self.result_paths = []
        
        self.configure_styles()
        self.setup_ui()
        self.load_initial_nodes()
        
        self.transient(parent)
        self.grab_set()
        self.parent = parent

    def configure_styles(self):
        style = ttk.Style()
        style.configure("Treeview", 
                        font=("Microsoft YaHei UI", 11), 
                        rowheight=32)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 11, "bold"))

    def setup_ui(self):
        top_frame = tk.Frame(self, bg="#f0f0f0", pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        
        lbl_title = tk.Label(top_frame, text="请选择文件夹", font=("Microsoft YaHei UI", 12, "bold"), bg="#f0f0f0")
        lbl_title.pack(anchor=tk.W, padx=15)
        
        lbl_hint = tk.Label(top_frame, text="提示: 点击箭头展开。按住 Ctrl 键点击可多选。", font=("Microsoft YaHei UI", 10), fg="#555", bg="#f0f0f0")
        lbl_hint.pack(anchor=tk.W, padx=15)

        btn_frame = ttk.Frame(self, padding=15)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        confirm_btn = ttk.Button(btn_frame, text="✅ 确定添加", command=self.on_confirm)
        confirm_btn.pack(side=tk.RIGHT, padx=5)

        tree_frame = ttk.Frame(self, padding=(15, 0, 15, 0))
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, selectmode='extended', yscrollcommand=scrollbar.set, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        self.tree.bind('<<TreeviewOpen>>', self.on_expand)
        self.tree.bind('<Double-1>', self.on_double_click)

    def load_initial_nodes(self):
        qa_node = self.tree.insert('', 'end', text="⭐ 快速访问 (Quick Access)", open=True)
        desktop = Path.home() / "Desktop"
        self._insert_node(qa_node, desktop, "🖥️ 桌面", is_dummy=False)
        current_dir = Path.cwd()
        self._insert_node(qa_node, current_dir, "📍 当前代码目录", is_dummy=False)

        pc_node = self.tree.insert('', 'end', text="💻 此电脑 (My Computer)", open=True)
        system = platform.system()
        if system == "Windows":
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
            for drive in drives:
                self._insert_node(pc_node, Path(drive), f"💿 本地磁盘 ({drive})")
        else:
            self._insert_node(pc_node, Path("/"), "💿 根目录 (/)")

    def _insert_node(self, parent, path_obj, display_text, is_dummy=True):
        node = self.tree.insert(parent, 'end', text=display_text, values=[str(path_obj)], open=False)
        if is_dummy:
            self.tree.insert(node, 'end', text="loading...")
        else:
            self.tree.insert(node, 'end', text="loading...")

    def on_expand(self, event):
        item_id = self.tree.focus()
        self._load_children(item_id)

    def on_double_click(self, event):
        item_id = self.tree.identify('item', event.x, event.y)
        if item_id:
            self._load_children(item_id)

    def _load_children(self, item_id):
        if not item_id: return
        values = self.tree.item(item_id, 'values')
        if not values: return
        parent_path = values[0]
        children = self.tree.get_children(item_id)
        if children:
            if self.tree.item(children[0], 'text') != "loading...":
                return
            self.tree.delete(*children)

        try:
            with os.scandir(parent_path) as it:
                entries = sorted([e for e in it if e.is_dir()], key=lambda s: s.name.lower())
            if not entries:
                self.tree.insert(item_id, 'end', text="(空文件夹)", values=[], tags=('gray',))
                return
            for entry in entries:
                try:
                    node = self.tree.insert(item_id, 'end', text=f"📂 {entry.name}", values=[entry.path], open=False)
                    self.tree.insert(node, 'end', text="loading...")
                except Exception:
                    continue
        except PermissionError:
            self.tree.insert(item_id, 'end', text="🚫 [权限拒绝]", values=[], tags=('error',))

    def on_confirm(self):
        selected_items = self.tree.selection()
        paths = []
        for item in selected_items:
            values = self.tree.item(item, 'values')
            if values:
                paths.append(values[0])
        self.result_paths = paths
        self.destroy()


# =============================================================================
#  主程序
# =============================================================================
class DirectoryTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件夹目录树生成器 v3.3 (支持拖拽)")
        self.root.geometry("1100x850")
        
        self.selected_paths = []
        
        # 依赖检查弹窗
        if not HAS_DND:
            messagebox.showwarning(
                "功能受限", 
                "未检测到 'tkinterdnd2' 库，拖拽功能无法使用。\n\n"
                "请运行: pip install tkinterdnd2\n"
                "然后重启本程序即可启用拖拽功能。"
            )

        self.configure_styles()
        self.setup_ui()
        self.setup_dnd() # 设置拖拽

    def configure_styles(self):
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=11, family="Microsoft YaHei UI")
        self.text_font = ("Consolas", 12)
        
        style = ttk.Style()
        style.theme_use('vista' if platform.system() == 'Windows' else 'clam')
        style.configure("TButton", font=("Microsoft YaHei UI", 11), padding=6)
        style.configure("TLabel", font=("Microsoft YaHei UI", 11))
        style.configure("TLabelframe", background="#f9f9f9")
        style.configure("TLabelframe.Label", font=("Microsoft YaHei UI", 12, "bold"), foreground="#333333", background="#f9f9f9")

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#f9f9f9")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 顶部控制区 ---
        control_frame = ttk.LabelFrame(main_frame, text="操作面板", padding="15")
        control_frame.pack(fill=tk.X, padx=20, pady=15)

        # 按钮栏
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="📂 添加文件夹", command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✨ 树状图选择", command=self.open_multi_selector).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🧹 清空列表", command=self.clear_list).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        self.scan_btn = ttk.Button(btn_frame, text="🚀 生成目录树", command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=8)
        
        self.save_btn = ttk.Button(btn_frame, text="💾 导出结果为TXT", command=self.save_to_file, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=8)

        # 路径显示
        list_header_frame = tk.Frame(control_frame, bg="#f9f9f9")
        list_header_frame.pack(fill=tk.X, pady=(15, 5))
        
        # 提示语根据是否支持拖拽变化
        hint_text = "待处理目录列表 (可将文件夹直接拖入下方区域):" if HAS_DND else "待处理目录列表:"
        tk.Label(list_header_frame, text=hint_text, font=("Microsoft YaHei UI", 11, "bold"), bg="#f9f9f9", fg="#444").pack(side=tk.LEFT)
        tk.Label(list_header_frame, text="(双击项目可移除)", font=("Microsoft YaHei UI", 9), bg="#f9f9f9", fg="#888").pack(side=tk.LEFT, padx=10)
        
        self.path_listbox = tk.Listbox(
            control_frame, 
            height=4, 
            selectmode=tk.EXTENDED, 
            bd=0, 
            highlightthickness=1,
            highlightbackground="#ddd",
            activestyle='none', 
            font=("Microsoft YaHei UI", 11),
            bg="white",
            selectbackground="#0078D7", 
            selectforeground="white"
        )
        self.path_listbox.pack(fill=tk.X, pady=0)
        self.path_listbox.bind('<Double-1>', self.remove_selected_path)

        # --- 底部结果展示区 ---
        result_frame = ttk.LabelFrame(main_frame, text="结果预览", padding="15")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.result_text = scrolledtext.ScrolledText(
            result_frame, 
            wrap=tk.NONE, 
            font=self.text_font,
            bd=0,
            highlightthickness=1,
            highlightbackground="#ddd"
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # --- 状态栏 ---
        self.status_var = tk.StringVar()
        msg = "准备就绪。请拖入或添加文件夹。" if HAS_DND else "准备就绪。请添加文件夹。"
        self.status_var.set(msg)
        
        status_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(status_frame, textvariable=self.status_var, bg="#e0e0e0", fg="#333", font=("Microsoft YaHei UI", 10), anchor=tk.W, padx=10).pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------------------
    # 核心新功能：拖拽处理
    # -------------------------------------------------------------------------
    def setup_dnd(self):
        if HAS_DND:
            # 注册 Drop 目标
            self.path_listbox.drop_target_register(DND_FILES)
            # 绑定事件
            self.path_listbox.dnd_bind('<<Drop>>', self.handle_drop)
            
            # 为了更好的体验，给主窗口的 frame 也绑定，这样拖到空白处也生效
            # 注意：frame 需要重新注册一次
            # 这里为了简单，仅绑定列表框，避免事件冲突
            
    def handle_drop(self, event):
        """处理拖放文件事件"""
        if not event.data:
            return
            
        # TkinterDnD 返回的数据在包含空格路径时会用 {} 包裹
        # 使用 tk.splitlist 可以完美解析这种 Tcl 格式的列表
        files = self.root.tk.splitlist(event.data)
        
        added_count = 0
        for p in files:
            # 清理路径可能存在的某些奇怪字符（视系统而定，一般 splitlist 已处理好）
            clean_path = p.strip()
            if os.path.isdir(clean_path):
                if self._add_path_to_list(clean_path):
                    added_count += 1
            elif os.path.isfile(clean_path):
                # 如果用户拖入的是文件，可以选择忽略，或者添加其父文件夹
                # 这里我们选择忽略并提示
                pass 
        
        if added_count > 0:
            self.status_var.set(f"✅ 已通过拖拽添加 {added_count} 个文件夹。")
        else:
            self.status_var.set("⚠️ 未添加新目录（可能不是文件夹或已存在）。")

    # -------------------------------------------------------------------------
    # 原有逻辑功能
    # -------------------------------------------------------------------------
    def open_multi_selector(self):
        dialog = MultiFolderSelector(self.root)
        self.root.wait_window(dialog)
        
        paths = dialog.result_paths
        if paths:
            count = 0
            for p in paths:
                if self._add_path_to_list(p):
                    count += 1
            if count > 0:
                self.status_var.set(f"✅ 已批量添加 {count} 个目录。")
            else:
                self.status_var.set("⚠️ 所选目录已在列表中。")

    def add_directory(self):
        path = filedialog.askdirectory(title="选择要扫描的文件夹")
        if path:
            if self._add_path_to_list(path):
                self.status_var.set(f"✅ 已添加: {Path(path).name}")

    def _add_path_to_list(self, path_str):
        path_obj = Path(path_str)
        resolved_path = str(path_obj.resolve())
        
        if resolved_path not in self.selected_paths:
            self.selected_paths.append(resolved_path)
            self.path_listbox.insert(tk.END, f" 📂 {resolved_path}")
            return True
        return False

    def remove_selected_path(self, event):
        selection = self.path_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_paths.pop(index)
            self.path_listbox.delete(index)
            self.status_var.set("已移除选中目录。")

    def clear_list(self):
        self.selected_paths.clear()
        self.path_listbox.delete(0, tk.END)
        self.status_var.set("列表已清空。")

    def start_scan(self):
        if not self.selected_paths:
            messagebox.showwarning("提示", "请先添加至少一个文件夹！")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.status_var.set("⏳ 正在扫描中，请稍候...")
        self.root.update()

        self.result_text.delete(1.0, tk.END)
        final_output = []
        
        try:
            for idx, path_str in enumerate(self.selected_paths):
                if idx > 0:
                    final_output.append("\n" + "="*60 + "\n")
                tree_str = self.generate_tree_string(path_str)
                final_output.append(tree_str)
            
            full_text = "\n".join(final_output)
            self.result_text.insert(tk.END, full_text)
            self.save_btn.config(state=tk.NORMAL)
            self.status_var.set(f"✅ 扫描完成。包含 {len(self.selected_paths)} 个根目录。")
            
        except Exception as e:
            messagebox.showerror("错误", f"扫描错误: {str(e)}")
            self.status_var.set("❌ 扫描出错")
        finally:
            self.scan_btn.config(state=tk.NORMAL)

    def generate_tree_string(self, root_path):
        output_lines = []
        root_dir = Path(root_path)
        stats = {'dirs': 0, 'files': 0}

        if not root_dir.exists():
            return f"❌ 错误: 路径不存在: {root_path}"

        output_lines.append(f"📁 {root_dir.name} ({root_dir.resolve()})")

        def _walk(directory, prefix=""):
            try:
                contents = list(directory.iterdir())
            except PermissionError:
                output_lines.append(f"{prefix}└── 🚫 [无访问权限]")
                return

            contents.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            pointers = ["├── ", "└── "]

            for index, path in enumerate(contents):
                is_last = (index == len(contents) - 1)
                connector = pointers[1] if is_last else pointers[0]

                if path.is_dir():
                    stats['dirs'] += 1
                    output_lines.append(f"{prefix}{connector}📂 {path.name}")
                    extension = "    " if is_last else "│   "
                    _walk(path, prefix + extension)
                else:
                    stats['files'] += 1
                    output_lines.append(f"{prefix}{connector}📄 {path.name}")

        _walk(root_dir)
        output_lines.append(f"\n📊 统计: {stats['dirs']} 个文件夹, {stats['files']} 个文件")
        return "\n".join(output_lines)

    def save_to_file(self):
        content = self.result_text.get(1.0, tk.END)
        if not content.strip():
            return

        SAFE_LENGTH_LIMIT = 150
        PREFIX = "目录树_"
        
        default_name = f"{PREFIX}结构.txt"
        
        if self.selected_paths:
            folder_names = [Path(p).name for p in self.selected_paths]
            full_joined_name = "+".join(folder_names)
            
            if len(PREFIX) + len(full_joined_name) <= SAFE_LENGTH_LIMIT:
                default_name = f"{PREFIX}{full_joined_name}.txt"
            else:
                current_name = ""
                count = 0
                for name in folder_names:
                    if len(PREFIX) + len(current_name) + len(name) + 25 > SAFE_LENGTH_LIMIT:
                        break
                    if current_name:
                        current_name += "+" + name
                    else:
                        current_name = name
                    count += 1
                
                remaining = len(folder_names) - count
                if remaining > 0:
                    default_name = f"{PREFIX}{current_name}+等{remaining}个目录.txt"
                else:
                    default_name = f"{PREFIX}{current_name}.txt"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="导出目录树"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("成功", f"文件已保存")
                self.status_var.set(f"✅ 文件已保存: {file_path}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))

if __name__ == "__main__":
    if HAS_DND:
        # 使用支持拖拽的 Tk 类
        root = TkinterDnD.Tk()
    else:
        # 降级使用普通 Tk 类
        root = tk.Tk()
        
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = DirectoryTreeApp(root)
    root.mainloop()