import tkinter as tk
from tkinter import colorchooser

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画图程序")

        # 默认参数
        self.current_tool = 'pencil'
        self.stroke_size = 5
        self.eraser_mode = 'area'  # 可选值：'area' 或 'stroke'
        self.color = 'black'
        self.last_x, self.last_y = None, None
        self.stroke_id = 0  # 用于给每个笔画分配唯一的ID

        # 光标可视化
        self.cursor_circle = None

        # 撤销/重做栈
        self.undo_stack = []
        self.redo_stack = []

        # 创建左侧工具栏
        self.create_toolbar()

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 绑定事件
        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_paint)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.canvas.bind('<Enter>', self.on_mouse_enter)
        self.canvas.bind('<Leave>', self.on_mouse_leave)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # 撤销/重做按钮
        undo_btn = tk.Button(toolbar, text='← 撤销', command=self.undo)
        undo_btn.pack(pady=5)
        redo_btn = tk.Button(toolbar, text='重做 →', command=self.redo)
        redo_btn.pack(pady=5)

        # 大小输入框和微调按钮，放在铅笔上方
        size_frame = tk.Frame(toolbar)
        size_frame.pack(pady=5)
        size_label = tk.Label(size_frame, text='笔尖/橡皮大小:')
        size_label.pack(side=tk.LEFT)
        self.size_spinbox = tk.Spinbox(size_frame, from_=1, to=100, width=5, command=self.update_cursor_size)
        self.size_spinbox.delete(0, 'end')
        self.size_spinbox.insert(0, '5')
        self.size_spinbox.pack(side=tk.LEFT)

        # 工具列表，调整顺序
        self.tools = ['颜色', '铅笔', '钢笔', '水彩笔', '橡皮', '切换橡皮模式', '清空']
        self.tool_buttons = {}
        self.indicators = {}

        for tool in self.tools:
            frame = tk.Frame(toolbar)
            frame.pack(pady=5)

            # 指示灯，改为圆形橙色
            indicator_canvas = tk.Canvas(frame, width=16, height=16, highlightthickness=0)
            indicator_canvas.pack(side=tk.LEFT)
            if tool == '颜色':
                # 颜色指示灯显示当前颜色，始终亮着
                indicator_circle = indicator_canvas.create_oval(2, 2, 14, 14, fill=self.color, outline='')
            else:
                indicator_circle = indicator_canvas.create_oval(2, 2, 14, 14, fill='lightgray', outline='')

            self.indicators[tool] = (indicator_canvas, indicator_circle)

            # 按钮
            if tool == '清空':
                btn = tk.Button(frame, text=tool, command=self.clear_canvas)
            elif tool == '铅笔':
                btn = tk.Button(frame, text=tool, command=lambda: self.select_tool('pencil'))
            elif tool == '钢笔':
                btn = tk.Button(frame, text=tool, command=lambda: self.select_tool('pen'))
            elif tool == '水彩笔':
                btn = tk.Button(frame, text=tool, command=lambda: self.select_tool('brush'))
            elif tool == '橡皮':
                btn = tk.Button(frame, text=tool, command=self.select_eraser)
            elif tool == '切换橡皮模式':
                btn = tk.Button(frame, text=tool, command=self.toggle_eraser_mode)
            elif tool == '颜色':
                btn = tk.Button(frame, text=tool, command=self.choose_color)
            btn.pack(side=tk.LEFT)

            self.tool_buttons[tool] = btn

            # 在“切换橡皮模式”按钮下方显示当前模式
            if tool == '切换橡皮模式':
                self.eraser_mode_label = tk.Label(toolbar, text=f"当前模式: {self.eraser_mode}")
                self.eraser_mode_label.pack(pady=2)

    def update_indicators(self):
        # 更新指示灯状态
        for tool in self.tools:
            indicator_canvas, indicator_circle = self.indicators[tool]
            if tool == '清空' or tool == '切换橡皮模式':
                continue
            elif tool == '颜色':
                # 颜色指示灯始终显示当前颜色
                indicator_canvas.itemconfig(indicator_circle, fill=self.color)
            elif tool == '橡皮' and self.current_tool == 'eraser':
                indicator_canvas.itemconfig(indicator_circle, fill='orange')
            elif tool == '铅笔' and self.current_tool == 'pencil':
                indicator_canvas.itemconfig(indicator_circle, fill='orange')
            elif tool == '钢笔' and self.current_tool == 'pen':
                indicator_canvas.itemconfig(indicator_circle, fill='orange')
            elif tool == '水彩笔' and self.current_tool == 'brush':
                indicator_canvas.itemconfig(indicator_circle, fill='orange')
            else:
                indicator_canvas.itemconfig(indicator_circle, fill='lightgray')

    def flash_indicator(self, tool):
        # 指示灯闪烁一秒
        indicator_canvas, indicator_circle = self.indicators[tool]
        indicator_canvas.itemconfig(indicator_circle, fill='orange')
        self.root.after(1000, lambda: indicator_canvas.itemconfig(indicator_circle, fill='lightgray'))

    def select_tool(self, tool):
        self.current_tool = tool
        self.update_indicators()
        self.update_cursor_size()

    def select_eraser(self):
        self.current_tool = 'eraser'
        self.update_indicators()
        self.update_cursor_size()

    def toggle_eraser_mode(self):
        if self.eraser_mode == 'area':
            self.eraser_mode = 'stroke'
        else:
            self.eraser_mode = 'area'
        self.eraser_mode_label.config(text=f"当前模式: {self.eraser_mode}")

    def choose_color(self):
        color = colorchooser.askcolor(color=self.color)[1]
        if color:
            self.color = color
            self.update_indicators()
            self.update_cursor_size()

    def clear_canvas(self):
        self.canvas.delete('all')
        self.flash_indicator('清空')
        self.cursor_circle = None  # 清空后需要重新创建光标可视化
        # 清空撤销/重做栈
        self.undo_stack.clear()
        self.redo_stack.clear()

    def on_button_press(self, event):
        self.stroke_size = int(self.size_spinbox.get())
        self.last_x, self.last_y = event.x, event.y

        # 开始新的笔画
        self.stroke_id += 1
        self.current_stroke_tag = f'stroke_{self.stroke_id}'
        self.current_stroke_items = []

        if self.current_tool == 'eraser' and self.eraser_mode == 'stroke':
            # 擦除整笔
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item in items:
                tags = self.canvas.gettags(item)
                if 'stroke' in tags:
                    stroke_tag = [tag for tag in tags if tag.startswith('stroke_')]
                    if stroke_tag:
                        self.erase_stroke(stroke_tag[0])

    def on_paint(self, event):
        x, y = event.x, event.y
        if self.current_tool == 'eraser' and self.eraser_mode == 'area':
            # 擦除经过的区域
            line = self.canvas.create_line(self.last_x, self.last_y, x, y,
                                           width=self.stroke_size, fill='white',
                                           capstyle=tk.ROUND, smooth=True)
            self.current_stroke_items.append(line)
        elif self.current_tool == 'eraser' and self.eraser_mode == 'stroke':
            # 擦除整笔（拖动时）
            items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
            for item in items:
                tags = self.canvas.gettags(item)
                if 'stroke' in tags:
                    stroke_tag = [tag for tag in tags if tag.startswith('stroke_')]
                    if stroke_tag:
                        self.erase_stroke(stroke_tag[0])
        else:
            # 绘制笔画
            if self.current_tool == 'pencil':
                width = self.stroke_size
                fill = self.color
                # 铅笔效果：细线
                line = self.canvas.create_line(self.last_x, self.last_y, x, y,
                                               width=width, fill=fill,
                                               capstyle=tk.ROUND, smooth=True,
                                               tags=('stroke', self.current_stroke_tag))
                self.current_stroke_items.append(line)
            elif self.current_tool == 'pen':
                width = self.stroke_size * 1.5
                fill = self.color
                # 钢笔效果：中等粗细
                line = self.canvas.create_line(self.last_x, self.last_y, x, y,
                                               width=width, fill=fill,
                                               capstyle=tk.ROUND, smooth=True,
                                               tags=('stroke', self.current_stroke_tag))
                self.current_stroke_items.append(line)
            elif self.current_tool == 'brush':
                width = self.stroke_size * 2
                fill = self.color
                # 水彩笔效果：模拟更明显的模糊边缘
                for i in range(5):
                    adjusted_width = width * (1 - 0.15 * i)
                    color = self.adjust_color_brightness(fill, 1 + 0.1 * i)
                    line = self.canvas.create_line(self.last_x, self.last_y, x, y,
                                                   width=adjusted_width, fill=color,
                                                   capstyle=tk.ROUND, smooth=True,
                                                   tags=('stroke', self.current_stroke_tag))
                    self.current_stroke_items.append(line)
            else:
                width = self.stroke_size
                fill = self.color

        self.last_x, self.last_y = x, y

    def on_button_release(self, event):
        self.last_x, self.last_y = None, None
        if self.current_stroke_items:
            self.save_undo(self.current_stroke_items)

    def adjust_color_brightness(self, color, factor):
        # 调整颜色亮度的辅助函数
        import colorsys
        r, g, b = self.root.winfo_rgb(color)
        r /= 65535
        g /= 65535
        b /= 65535
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = max(0, min(1, l * factor))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        r = int(r * 65535)
        g = int(g * 65535)
        b = int(b * 65535)
        return f'#{r:04x}{g:04x}{b:04x}'

    def on_mouse_move(self, event):
        # 更新光标可视化的位置和大小
        x, y = event.x, event.y
        size = int(self.size_spinbox.get())
        if self.current_tool == 'pencil':
            width = size
            outline = self.color
        elif self.current_tool == 'pen':
            width = size * 1.5
            outline = self.color
        elif self.current_tool == 'brush':
            width = size * 2
            outline = self.color
        elif self.current_tool == 'eraser':
            width = size
            outline = 'gray'
        else:
            width = size
            outline = self.color

        radius = width / 2

        if self.cursor_circle:
            self.canvas.coords(self.cursor_circle, x - radius, y - radius, x + radius, y + radius)
            self.canvas.itemconfig(self.cursor_circle, outline=outline)
        else:
            self.cursor_circle = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                         outline=outline, width=1, tags='cursor')
            self.canvas.tag_raise('cursor')

    def on_mouse_enter(self, event):
        # 当鼠标进入画布时，显示光标可视化
        self.update_cursor_size()

    def on_mouse_leave(self, event):
        # 当鼠标离开画布时，隐藏光标可视化
        if self.cursor_circle:
            self.canvas.delete(self.cursor_circle)
            self.cursor_circle = None

    def update_cursor_size(self):
        # 更新光标可视化的大小
        if self.cursor_circle:
            size = int(self.size_spinbox.get())
            x, y = self.canvas.winfo_pointerxy()
            x -= self.canvas.winfo_rootx()
            y -= self.canvas.winfo_rooty()

            if self.current_tool == 'pencil':
                width = size
                outline = self.color
            elif self.current_tool == 'pen':
                width = size * 1.5
                outline = self.color
            elif self.current_tool == 'brush':
                width = size * 2
                outline = self.color
            elif self.current_tool == 'eraser':
                width = size
                outline = 'gray'
            else:
                width = size
                outline = self.color

            radius = width / 2

            self.canvas.coords(self.cursor_circle, x - radius, y - radius, x + radius, y + radius)
            self.canvas.itemconfig(self.cursor_circle, outline=outline)

        else:
            # 如果光标可视化不存在，创建一个
            x, y = self.canvas.winfo_pointerxy()
            x -= self.canvas.winfo_rootx()
            y -= self.canvas.winfo_rooty()
            self.on_mouse_move(tk.Event(x=x, y=y))

    def save_undo(self, items):
        # 保存操作以便撤销，items是item id列表
        stroke = []
        for item in items:
            item_type = self.canvas.type(item)
            coords = self.canvas.coords(item)
            options = self.canvas.itemconfig(item)
            item_options = {k: v[-1] for k, v in options.items()}
            stroke.append({'id': item, 'type': item_type, 'coords': coords, 'options': item_options})
        self.undo_stack.append(stroke)
        self.redo_stack.clear()

    def erase_stroke(self, stroke_tag):
        # 擦除整笔并保存以便撤销
        items = self.canvas.find_withtag(stroke_tag)
        stroke = []
        for item in items:
            item_type = self.canvas.type(item)
            coords = self.canvas.coords(item)
            options = self.canvas.itemconfig(item)
            item_options = {k: v[-1] for k, v in options.items()}
            stroke.append({'id': item, 'type': item_type, 'coords': coords, 'options': item_options})
        self.undo_stack.append(stroke)
        self.redo_stack.clear()
        for item in items:
            self.canvas.delete(item)

    def undo(self):
        if self.undo_stack:
            stroke = self.undo_stack.pop()
            # 删除画布上的项
            for item_data in stroke:
                item_id = item_data['id']
                self.canvas.delete(item_id)
            self.redo_stack.append(stroke)

    def redo(self):
        if self.redo_stack:
            stroke = self.redo_stack.pop()
            for item_data in stroke:
                item_type = item_data['type']
                coords = item_data['coords']
                options = item_data['options']
                # 移除标签以避免重复
                options.pop('tags', None)
                if item_type == 'line':
                    item_id = self.canvas.create_line(*coords, **options)
                elif item_type == 'oval':
                    item_id = self.canvas.create_oval(*coords, **options)
                # 更新item_id
                item_data['id'] = item_id
            self.undo_stack.append(stroke)

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
