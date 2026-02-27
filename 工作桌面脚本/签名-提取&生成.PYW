import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import platform
import glob

# --- 尝试导入拖拽支持库 ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("提示: 未安装 tkinterdnd2 库，拖拽功能不可用。请运行 pip install tkinterdnd2")

class SignatureExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("全能签名设计与提取器 (SVG/PNG)")
        self.root.geometry("1100x750")
        
        # 样式设置
        style = ttk.Style()
        style.theme_use('clam')
        
        # 状态变量
        self.original_cv_image = None  # 当前处理的OpenCV图像
        
        # 存储原始轮廓数据，用于导出时重新计算
        self.raw_contours = []
        self.raw_hierarchy = None
        
        self.processed_contours = []   # 用于预览的简化轮廓
        self.preview_image_tk = None   # 防止被垃圾回收
        self.source_image_tk = None    # 左侧原图预览
        self.is_text_mode = False      # 标记当前是否处于文字模式
        
        # --- 字体系统初始化 ---
        self.system_font_dir = self.get_system_font_dir()
        self.font_list = self.scan_fonts()
        # 优先寻找行楷
        default_font_file = self.find_preferred_font(["STXINGKA.TTF", "STXINGKA.GM", "SIMLI.TTF", "simkai.ttf", "msyh.ttc"])
        
        self.font_path = os.path.join(self.system_font_dir, default_font_file) if default_font_file else None
        self.loaded_font_name = default_font_file if default_font_file else "默认字体"
        
        # --- 布局设计 ---
        
        # 1. 顶部：公共参数控制
        self.setup_top_controls()

        # 2. 主区域：左右分栏
        main_paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # --- 左侧：输入源 ---
        left_container = ttk.Frame(main_paned)
        main_paned.add(left_container, weight=1)
        
        self.notebook = ttk.Notebook(left_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # 选项卡 1: 图片提取模式
        self.tab_image = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_image, text=" 📷 图片提取模式 ")
        self.setup_image_tab()
        
        # 选项卡 2: 文字生成模式
        self.tab_text = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_text, text=" ✍️ 文字生成模式 ")
        self.setup_text_tab()
        
        # --- 右侧：结果预览 ---
        right_frame = ttk.LabelFrame(main_paned, text="结果预览 (透明背景)", padding=5)
        main_paned.add(right_frame, weight=1)
        
        self.canvas_preview = tk.Canvas(right_frame, bg="white") 
        self.canvas_preview.pack(fill=tk.BOTH, expand=True)
        self.draw_checkerboard(self.canvas_preview)

        # 如果默认找到了字体，且在文字模式，初始化一次
        if self.font_path:
            self.notebook.select(self.tab_text)
            
        # 初始化拖拽 (全局)
        if HAS_DND: self.setup_dnd()

    # --- 字体逻辑 ---
    
    def get_system_font_dir(self):
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
        elif system == "Darwin":
            return "/System/Library/Fonts"
        else:
            return "/usr/share/fonts"

    def scan_fonts(self):
        fonts = []
        if os.path.exists(self.system_font_dir):
            extensions = ['*.ttf', '*.otf', '*.ttc', '*.TTF', '*.OTF', '*.TTC']
            for ext in extensions:
                found = [os.path.basename(f) for f in glob.glob(os.path.join(self.system_font_dir, ext))]
                fonts.extend(found)
        return sorted(fonts)

    def find_preferred_font(self, candidates):
        lower_fonts = [f.lower() for f in self.font_list]
        for cand in candidates:
            if cand.lower() in lower_fonts:
                idx = lower_fonts.index(cand.lower())
                return self.font_list[idx]
        return self.font_list[0] if self.font_list else None

    # --- 界面构建 ---

    def setup_top_controls(self):
        control_frame = ttk.LabelFrame(self.root, text="处理参数 (实时预览)", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # 保存按钮区 (合并为一个)
        self.btn_export = ttk.Button(control_frame, text="💾 导出结果", command=self.export_file, state=tk.DISABLED)
        self.btn_export.pack(side=tk.RIGHT, padx=10)

        # 参数滑块区域
        slider_frame = ttk.Frame(control_frame)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 阈值
        ttk.Label(slider_frame, text="墨迹浓度 (阈值):").grid(row=0, column=0, sticky=tk.W)
        # 修改：默认值改为 10 (最低)
        self.threshold_var = tk.IntVar(value=10) 
        self.slider_threshold = ttk.Scale(slider_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.threshold_var, command=lambda v: self.on_param_change())
        self.slider_threshold.grid(row=0, column=1, sticky=tk.EW, padx=5, ipadx=50)
        
        # 平滑度
        ttk.Label(slider_frame, text="线条平滑度:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.smoothness_var = tk.DoubleVar(value=0.1)
        self.slider_smooth = ttk.Scale(slider_frame, from_=0.1, to=8.0, orient=tk.HORIZONTAL, variable=self.smoothness_var, command=lambda v: self.on_param_change())
        self.slider_smooth.grid(row=0, column=3, sticky=tk.EW, padx=5, ipadx=50)

    def setup_image_tab(self):
        btn_frame = ttk.Frame(self.tab_image, padding=5)
        btn_frame.pack(fill=tk.X)
        
        btn_upload = ttk.Button(btn_frame, text="📂 上传图片", command=self.upload_image_dialog)
        btn_upload.pack(side=tk.LEFT)
        ttk.Label(btn_frame, text="(支持拖拽图片文件)").pack(side=tk.LEFT, padx=5)

        self.img_preview_frame = ttk.LabelFrame(self.tab_image, text="原图预览")
        self.img_preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.lbl_source_img = tk.Label(self.img_preview_frame, text="请拖入或上传图片", bg="#f0f0f0")
        self.lbl_source_img.pack(fill=tk.BOTH, expand=True)

    def setup_text_tab(self):
        container = ttk.Frame(self.tab_text, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # 1. 文本输入
        ttk.Label(container, text="输入签名文本 (支持拖拽字体文件):").pack(anchor=tk.W)
        self.entry_text = ttk.Entry(container, font=("Arial", 14))
        self.entry_text.insert(0, "楚昊然") # 默认文本
        self.entry_text.pack(fill=tk.X, pady=(0, 10))
        self.entry_text.bind("<KeyRelease>", lambda e: self.on_text_param_change())
        
        # 2. 字体选择
        font_frame = ttk.LabelFrame(container, text="字体选择", padding=5)
        font_frame.pack(fill=tk.X, pady=5)
        
        self.font_combo = ttk.Combobox(font_frame, values=self.font_list, state="readonly", height=20)
        self.font_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.loaded_font_name in self.font_list:
            self.font_combo.set(self.loaded_font_name)
        self.font_combo.bind("<<ComboboxSelected>>", self.on_font_selected)
        
        btn_load_custom = ttk.Button(font_frame, text="📂 自定义", width=8, command=self.load_custom_font)
        btn_load_custom.pack(side=tk.RIGHT, padx=(5,0))
        
        # 3. 文字属性滑块
        props_frame = ttk.LabelFrame(container, text="排版属性 (实时)", padding=5)
        props_frame.pack(fill=tk.X, pady=10)
        
        # 字号
        ttk.Label(props_frame, text="字号大小:").grid(row=0, column=0, sticky=tk.W)
        self.font_size_var = tk.IntVar(value=400) # 默认最大
        scale_size = ttk.Scale(props_frame, from_=50, to=400, variable=self.font_size_var, orient=tk.HORIZONTAL, command=lambda v: self.on_text_param_change())
        scale_size.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # 字距
        ttk.Label(props_frame, text="字符间距:").grid(row=1, column=0, sticky=tk.W)
        # 修改：默认值改为 -100 (最低)
        self.font_spacing_var = tk.IntVar(value=-100) 
        scale_spacing = ttk.Scale(props_frame, from_=-100, to=100, variable=self.font_spacing_var, orient=tk.HORIZONTAL, command=lambda v: self.on_text_param_change())
        scale_spacing.grid(row=1, column=1, sticky=tk.EW, padx=5)
        
        # 字体粗细
        ttk.Label(props_frame, text="字体粗细 (左侧细-右侧粗):").grid(row=2, column=0, sticky=tk.W)
        self.font_weight_var = tk.DoubleVar(value=50.0)
        # 这里使用 DoubleVar 配合 Scale 已经是高精度的浮点数，
        # 关键是后端的渲染逻辑需要支持高精度，不能只是 int() 截断
        scale_weight = ttk.Scale(props_frame, from_=0, to=100, variable=self.font_weight_var, orient=tk.HORIZONTAL, command=lambda v: self.on_text_param_change())
        scale_weight.grid(row=2, column=1, sticky=tk.EW, padx=5)

        props_frame.columnconfigure(1, weight=1)
        
        # 说明
        info_lbl = tk.Label(container, text="💡 提示：\n• 已启用 3x 超采样技术，字体粗细调节实现“亚像素级”丝滑。\n• 默认保存格式已调整为 PNG 透明图片。", 
                            justify=tk.LEFT, fg="gray", bg="#f0f0f0")
        info_lbl.pack(fill=tk.X, pady=20)
        
        # 初始触发一次生成
        self.root.after(500, self.on_text_param_change)

    # --- 事件处理 ---

    def on_tab_change(self, event):
        current_tab = self.notebook.select()
        if current_tab == str(self.tab_text):
            self.is_text_mode = True
            self.on_text_param_change()
        else:
            self.is_text_mode = False
            if self.original_cv_image is not None:
                self.update_preview()

    def on_font_selected(self, event):
        selected_font = self.font_combo.get()
        self.font_path = os.path.join(self.system_font_dir, selected_font)
        self.on_text_param_change()

    def on_text_param_change(self):
        if not self.is_text_mode: return
        self.generate_text_signature(silent=True)

    def on_param_change(self):
        self.update_preview()

    # --- 核心逻辑 ---

    def generate_text_signature(self, silent=False):
        text = self.entry_text.get()
        if not text: return
            
        base_size = self.font_size_var.get()
        base_spacing = self.font_spacing_var.get()
        weight_percent = self.font_weight_var.get()
        
        # --- 超采样逻辑 (Supersampling) ---
        # 我们在 3 倍分辨率下进行绘制和粗细处理，然后再缩小
        # 这样可以将粗细的调整颗粒度提升 3 倍，解决 1px 跳变的问题
        SCALE_FACTOR = 3
        
        scaled_size = base_size * SCALE_FACTOR
        scaled_spacing = base_spacing * SCALE_FACTOR
        
        stroke_width = 0
        erode_pixels = 0
        
        # 重新计算粗细参数，基于放大后的尺寸
        if weight_percent > 50:
            factor = (weight_percent - 50) / 50.0
            # 系数微调，确保最大粗细合理
            stroke_width = int(scaled_size * factor * 0.05)
        elif weight_percent < 50:
            factor = (50 - weight_percent) / 50.0
            erode_pixels = int(scaled_size * factor * 0.03)
            # 在超采样模式下，即便算出来是 1 或 2 px，缩放回去也是亚像素级别的变细
        
        try:
            font = None
            if self.font_path:
                try: font = ImageFont.truetype(self.font_path, scaled_size)
                except: pass
            if font is None: font = ImageFont.load_default()
                
            total_width = 0
            max_height = 0
            dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
            char_dims = []
            
            # 计算文字尺寸
            for char in text:
                check_stroke = stroke_width if stroke_width > 0 else 0
                bbox = dummy_draw.textbbox((0, 0), char, font=font, stroke_width=check_stroke)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w <= 0: w = scaled_size // 2
                if h <= 0: h = scaled_size
                char_dims.append((w, h))
                total_width += w + scaled_spacing
                max_height = max(max_height, h)
            
            if text: total_width -= scaled_spacing
            
            padding = 50 * SCALE_FACTOR
            img_w = max(100 * SCALE_FACTOR, int(total_width + padding * 2))
            img_h = max(100 * SCALE_FACTOR, int(max_height * 2.5 + padding * 2))
            
            # 1. 绘制高清大图
            pil_image = Image.new("RGB", (img_w, img_h), "white")
            draw = ImageDraw.Draw(pil_image)
            
            current_x = padding
            baseline_y = img_h // 2 - max_height // 2
            
            for i, char in enumerate(text):
                w, h = char_dims[i]
                if stroke_width > 0:
                    draw.text((current_x, baseline_y), char, font=font, fill="black", stroke_width=stroke_width, stroke_fill="black")
                else:
                    draw.text((current_x, baseline_y), char, font=font, fill="black")
                current_x += w + scaled_spacing
            
            open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # 2. 应用高清腐蚀 (变细)
            if erode_pixels > 0:
                kernel = np.ones((3, 3), np.uint8)
                open_cv_image = cv2.dilate(open_cv_image, kernel, iterations=erode_pixels)

            # 3. 高质量缩小回目标尺寸 (Downsampling)
            # 使用 INTER_AREA 插值，它是最适合缩小的算法，能保留灰度细节
            target_w = img_w // SCALE_FACTOR
            target_h = img_h // SCALE_FACTOR
            
            final_image = cv2.resize(open_cv_image, (target_w, target_h), interpolation=cv2.INTER_AREA)

            self.original_cv_image = final_image
            
            self.btn_export.config(state=tk.NORMAL)
            self.update_preview()
            
            if not silent: messagebox.showinfo("成功", "生成完毕")
                
        except Exception as e:
            if not silent: messagebox.showerror("错误", f"生成失败: {e}")
    
    def process_image(self):
        """处理图像并保留原始轮廓数据"""
        if self.original_cv_image is None: return None, None
        
        gray = cv2.cvtColor(self.original_cv_image, cv2.COLOR_BGR2GRAY)
        thresh_val = self.threshold_var.get()
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
        kernel = np.ones((2,2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 核心：使用 RETR_TREE 保留层级，并存储到 self 中供导出使用
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        self.raw_contours = contours
        self.raw_hierarchy = hierarchy
        
        return binary, contours

    def update_preview(self, event=None):
        if self.original_cv_image is None: return
        binary, contours = self.process_image()
        h, w = binary.shape
        
        epsilon_factor = self.smoothness_var.get()
        self.processed_contours = [] 
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 5: continue
            epsilon = epsilon_factor * 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            self.processed_contours.append(approx)
            
        display_canvas = np.ones((h, w, 3), dtype=np.uint8) * 255
        cv2.drawContours(display_canvas, self.processed_contours, -1, (0, 0, 0), -1)
        self.display_image(display_canvas, self.canvas_preview, is_preview=True)

    def display_image(self, cv_img, widget, is_preview=False):
        h, w = cv_img.shape[:2]
        display_w = widget.winfo_width()
        display_h = widget.winfo_height()
        if display_w < 50: display_w = 400
        if display_h < 50: display_h = 400
        scale = min(display_w/w, display_h/h)
        new_w, new_h = int(w*scale), int(h*scale)
        resized = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        rgb_img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        tk_img = ImageTk.PhotoImage(pil_img)
        
        if is_preview:
            self.preview_image_tk = tk_img
            widget.delete("img_tag")
            widget.create_image(display_w//2, display_h//2, image=tk_img, tags="img_tag")
        else:
            self.source_image_tk = tk_img
            widget.config(image=tk_img, text="")

    # --- 统一导出入口 ---
    def export_file(self):
        """统一导出函数，根据文件类型分发"""
        if not self.processed_contours: return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            # 关键修改：将 PNG 放在第一个，作为默认选项
            filetypes=[("PNG 透明图片", "*.png"), ("SVG 矢量图", "*.svg")]
        )
        if not file_path: return

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == ".svg":
            self._write_svg(file_path)
        elif ext == ".png":
            self._write_png(file_path)
        else:
            # 默认兜底
            self._write_png(file_path + ".png")

    def _write_svg(self, filename):
        h, w = self.original_cv_image.shape[:2]
        all_path_data = []
        for cnt in self.processed_contours:
            if len(cnt) < 3: continue
            points = cnt.reshape(-1, 2)
            path_part = ["M", f"{points[0][0]} {points[0][1]}"]
            for p in points[1:]: path_part.append(f"L {p[0]} {p[1]}")
            path_part.append("Z")
            all_path_data.append(" ".join(path_part))
        full_d_string = " ".join(all_path_data)
        svg_content = [
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<!-- Generated by Python Signature Extractor -->',
            f'<path d="{full_d_string}" fill="black" stroke="none" fill-rule="evenodd" />',
            '</svg>'
        ]
        try:
            with open(filename, "w", encoding="utf-8") as f: f.write("\n".join(svg_content))
            messagebox.showinfo("成功", "SVG 文件已导出！")
        except Exception as e:
            messagebox.showerror("错误", f"{e}")

    def _write_png(self, filename):
        """稳健的PNG导出，修复之前可能的空文件问题 + 中文路径支持"""
        if not self.raw_contours or self.raw_hierarchy is None:
            messagebox.showwarning("警告", "没有内容可导出")
            return
            
        h, w = self.original_cv_image.shape[:2]
        
        # 构造全黑 + 透明 Alpha 的画布
        # B, G, R 通道全为 0 (黑色)
        b_channel = np.zeros((h, w), dtype=np.uint8)
        g_channel = np.zeros((h, w), dtype=np.uint8)
        r_channel = np.zeros((h, w), dtype=np.uint8)
        # Alpha 通道初始化为 0 (全透明)
        a_channel = np.zeros((h, w), dtype=np.uint8)
        
        epsilon_factor = self.smoothness_var.get()
        hierarchy = self.raw_hierarchy[0] # 获取层级数据
        
        # 分组：深度 -> 轮廓列表
        contours_by_depth = {}
        
        # 辅助函数：计算深度
        def get_depth(idx, hier):
            d = 0
            current_parent = hier[idx][3]
            while current_parent != -1:
                d += 1
                current_parent = hier[current_parent][3]
            return d

        # 遍历所有原始轮廓，重新计算平滑后的形状，并按深度分组
        for i, cnt in enumerate(self.raw_contours):
            area = cv2.contourArea(cnt)
            if area < 5: continue # 过滤噪点
            
            # 计算平滑
            epsilon = epsilon_factor * 0.001 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            depth = get_depth(i, hierarchy)
            if depth not in contours_by_depth:
                contours_by_depth[depth] = []
            contours_by_depth[depth].append(approx)
            
        # 按层级绘制到 Alpha 通道
        # 偶数层 (0, 2...) 画 255 (不透明/实体)
        # 奇数层 (1, 3...) 画 0   (透明/挖空)
        max_depth = max(contours_by_depth.keys()) if contours_by_depth else 0
        
        for d in range(max_depth + 1):
            if d in contours_by_depth:
                color = 255 if d % 2 == 0 else 0
                cv2.drawContours(a_channel, contours_by_depth[d], -1, color, -1)
                
        # 合并通道
        rgba = cv2.merge((b_channel, g_channel, r_channel, a_channel))
        
        try:
            # 修改：使用 cv2.imencode + open 写入，支持中文路径
            is_success, im_buf_arr = cv2.imencode(".png", rgba)
            if is_success:
                with open(filename, "wb") as f:
                    f.write(im_buf_arr)
                messagebox.showinfo("成功", "PNG 文件已导出！\n(背景透明，孔洞已处理)")
            else:
                raise Exception("图像编码失败")
        except Exception as e:
            messagebox.showerror("错误", f"PNG 导出失败: {e}")

    # --- DND ---
    def setup_dnd(self):
        try:
            self.tab_text.drop_target_register(DND_FILES)
            self.tab_text.dnd_bind('<<Drop>>', self.handle_drop)
            self.tab_image.drop_target_register(DND_FILES)
            self.tab_image.dnd_bind('<<Drop>>', self.handle_drop)
            self.lbl_source_img.drop_target_register(DND_FILES)
            self.lbl_source_img.dnd_bind('<<Drop>>', self.handle_drop)
            self.entry_text.drop_target_register(DND_FILES)
            self.entry_text.dnd_bind('<<Drop>>', self.handle_drop)
        except Exception: pass

    def handle_drop(self, event):
        file_path = event.data
        if not file_path: return
        if file_path.startswith('{') and file_path.endswith('}'): file_path = file_path[1:-1]
        elif ' ' in file_path and not os.path.exists(file_path):
            parts = file_path.split('} {')
            if parts: file_path = parts[0].strip('{}')
            
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            self.notebook.select(self.tab_image)
            self.load_image_from_file(file_path)
        elif ext in ['.ttf', '.otf', '.ttc']:
            self.notebook.select(self.tab_text)
            self.font_path = file_path
            self.font_combo.set(os.path.basename(file_path))
            self.on_text_param_change()
        else:
            messagebox.showwarning("格式不支持", f"不支持的文件格式: {ext}\n仅支持图片(.jpg/.png)或字体(.ttf/.otf)")

    def upload_image_dialog(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            valid_exts = {'.jpg', '.jpeg', '.png', '.bmp'}
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in valid_exts:
                messagebox.showerror("格式不支持", f"您选择的文件格式 ({ext}) 不受支持。\n请选择图片文件 (JPG/PNG/BMP)。")
                return
            self.load_image_from_file(file_path)

    def load_image_from_file(self, file_path):
        try:
            self.original_cv_image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if self.original_cv_image is None: raise Exception("解码失败")
            self.display_image(self.original_cv_image, self.lbl_source_img, is_preview=False)
            self.btn_export.config(state=tk.NORMAL)
            self.update_preview()
        except Exception as e: messagebox.showerror("错误", f"无法加载图片: {e}")

    def draw_checkerboard(self, canvas):
        canvas.update()
        w, h = 2000, 2000
        size = 20
        for y in range(0, h, size):
            for x in range(0, w, size):
                if (x // size + y // size) % 2 == 0:
                    canvas.create_rectangle(x, y, x+size, y+size, fill="#f0f0f0", outline="")
    
    def load_custom_font(self):
        font_path = filedialog.askopenfilename()
        if font_path:
            valid_exts = {'.ttf', '.otf', '.ttc'}
            _, ext = os.path.splitext(font_path)
            if ext.lower() not in valid_exts:
                messagebox.showerror("格式不支持", f"您选择的文件格式 ({ext}) 不受支持。\n请选择字体文件 (TTF/OTF/TTC)。")
                return

            self.font_path = font_path
            self.font_combo.set(os.path.basename(font_path))
            self.on_text_param_change()

if __name__ == "__main__":
    if HAS_DND: root = TkinterDnD.Tk()
    else: root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = SignatureExtractorApp(root)
    root.mainloop()