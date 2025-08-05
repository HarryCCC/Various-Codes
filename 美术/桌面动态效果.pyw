# -*- coding: utf-8 -*-
"""
桌面动态效果套件 - v8.0 (精简版)
一个交互式的桌面覆盖程序，提供多种可切换的背景效果。
本版根据用户要求，移除了“落英缤纷”效果及其所有相关代码。

依赖库:
pip install pystray pillow
"""

import tkinter as tk
import random
import math
import threading
from PIL import Image, ImageDraw, ImageTk
from pystray import MenuItem, Menu, Icon

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# 粒子类: 雪花
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
class Snowflake:
    def __init__(self, canvas, width, height, config):
        self.canvas = canvas; self.width = width; self.height = height
        self.config = config
        self.tk_object = None
        self.photo_image = None # 用于持有对PhotoImage的引用，防止被垃圾回收
        self.x = random.randint(0, self.width); self.y = random.randint(0, self.height)
        self.dx_accumulator = 0.0
        self.dy_accumulator = 0.0
        self.reset(); self.update_properties()

    def _create_snowflake_image(self):
        """预先将雪花绘制到一张PIL图片上"""
        img_size = int(self.size * 2.5)
        image = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        center = img_size // 2

        segments = []
        num_arms = 6
        style = self.style
        main_arm_length = self.size
        for i in range(num_arms):
            angle = (i * 360 / num_arms) * (math.pi / 180)
            p_end = (main_arm_length * math.cos(angle), main_arm_length * math.sin(angle))
            segments.append(((0, 0), p_end))
            if style == 'classic_V':
                branch_len = main_arm_length * 0.35
                angle1, angle2 = angle + 135 * (math.pi / 180), angle - 135 * (math.pi / 180)
                p_branch1 = (p_end[0] + branch_len * math.cos(angle1), p_end[1] + branch_len * math.sin(angle1))
                p_branch2 = (p_end[0] + branch_len * math.cos(angle2), p_end[1] + branch_len * math.sin(angle2))
                segments.append((p_end, p_branch1)); segments.append((p_end, p_branch2))
            elif style == 'diamond':
                p_mid = (main_arm_length * 0.8 * math.cos(angle), main_arm_length * 0.8 * math.sin(angle))
                branch_len = main_arm_length * 0.2
                angle1, angle2 = angle + 90 * (math.pi / 180), angle - 90 * (math.pi / 180)
                p_side1 = (p_mid[0] + branch_len * math.cos(angle1), p_mid[1] + branch_len * math.sin(angle1))
                p_side2 = (p_mid[0] + branch_len * math.cos(angle2), p_mid[1] + branch_len * math.sin(angle2))
                segments.append((p_side1, p_end)); segments.append((p_side2, p_end))
            elif style == 'multi_branch':
                for pos_factor in [0.4, 0.7]:
                    branch_len = main_arm_length * 0.3
                    p_start = (main_arm_length * pos_factor * math.cos(angle), main_arm_length * pos_factor * math.sin(angle))
                    angle1, angle2 = angle + 60 * (math.pi / 180), angle - 60 * (math.pi / 180)
                    p_b1 = (p_start[0] + branch_len * math.cos(angle1), p_start[1] + branch_len * math.sin(angle1))
                    p_b2 = (p_start[0] + branch_len * math.cos(angle2), p_start[1] + branch_len * math.sin(angle2))
                    segments.append((p_start, p_b1)); segments.append((p_start, p_b2))
        
        for p1, p2 in segments:
            draw.line(
                (p1[0] + center, p1[1] + center, p2[0] + center, p2[1] + center),
                fill=self.color,
                width=1
            )
        
        self.photo_image = ImageTk.PhotoImage(image)

    def destroy(self):
        try:
            if self.tk_object:
                self.canvas.delete(self.tk_object)
        except tk.TclError:
            pass

    def reset(self, y_pos=None):
        self.destroy()
        self.y = y_pos if y_pos is not None else random.randint(0, self.height)
        self.x = random.randint(0, self.width)
        self.dx_accumulator = 0.0
        self.dy_accumulator = 0.0
        self.size = random.uniform(2.5, 5.0) 
        self.color = random.choice(["#f0f8ff", "#e6e6fa", "#dcdcdc"])
        self.style = random.choice(['classic_V', 'diamond', 'multi_branch'])
        
        self._create_snowflake_image()
        self.tk_object = self.canvas.create_image(self.x, self.y, image=self.photo_image)
        
    def update_properties(self):
        self.speed_y = random.uniform(*self.config['snow_speed_range'])
        self.sway_amplitude = random.uniform(0, self.config['snow_sway_strength'])
        self.sway_frequency = random.uniform(0.04, 0.08)
        self.sway_offset = random.uniform(0, 2 * math.pi)

    def move(self, global_wind):
        if not self.tk_object: return
        self.y += self.speed_y
        sway_speed_x = self.sway_amplitude * math.sin(self.sway_frequency * self.y + self.sway_offset)
        self.x += sway_speed_x
        self.dy_accumulator += self.speed_y
        self.dx_accumulator += sway_speed_x
        move_x = int(self.dx_accumulator)
        move_y = int(self.dy_accumulator)
        if move_x != 0 or move_y != 0:
            try:
                self.canvas.move(self.tk_object, move_x, move_y)
                self.dx_accumulator -= move_x
                self.dy_accumulator -= move_y
            except tk.TclError:
                pass
        if self.y > self.height + self.size * 5:
            self.reset(y_pos=-self.size * 5)
            self.update_properties()

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# 粒子类: 雨滴
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
class Raindrop:
    def __init__(self, canvas, width, height, config):
        self.canvas = canvas; self.width = width; self.height = height
        self.config = config; self.tk_object = None
        self.dx_accumulator = 0.0
        self.dy_accumulator = 0.0
        self.reset()
        
    def destroy(self):
        try:
            if self.tk_object: self.canvas.delete(self.tk_object)
        except tk.TclError:
            pass
        self.tk_object = None

    def reset(self, y_pos=None):
        self.destroy()
        self.x = random.randint(0, self.width)
        self.y = y_pos if y_pos is not None else random.randint(-self.height, 0)
        self.dx_accumulator = 0.0
        self.dy_accumulator = 0.0
        self.color = random.choice(["gray80", "gray85", "gray90"])
        self.width_px = 1
        self.stipple = random.choice(['', 'gray75', 'gray50'])
        self.speed_x = random.uniform(-0.3, 0.3)
        self.update_properties()
        self.tk_object = self.canvas.create_line(
            self.x, self.y, self.x + self.length_x, self.y + self.length_y,
            fill=self.color, width=self.width_px, stipple=self.stipple)

    def update_properties(self):
        self.speed_y = random.uniform(*self.config['rain_speed_range'])
        self.length = self.speed_y * 0.4 * random.uniform(0.6, 2.0)
        self.length_x = self.length * (self.config.get('global_wind', 0) * 0.3 + self.speed_x * 0.2)
        self.length_y = self.length

    def move(self, global_wind):
        if not self.tk_object: return
        dx = global_wind + self.speed_x
        dy = self.speed_y
        self.x += dx
        self.y += dy
        self.dx_accumulator += dx
        self.dy_accumulator += dy
        move_x = int(self.dx_accumulator)
        move_y = int(self.dy_accumulator)
        if move_x != 0 or move_y != 0:
            try:
                self.length_x = self.length * (global_wind * 0.3 + self.speed_x * 0.2)
                self.canvas.move(self.tk_object, move_x, move_y)
                self.dx_accumulator -= move_x
                self.dy_accumulator -= move_y
            except tk.TclError:
                pass
        if self.y > self.height:
            self.reset(y_pos=-(self.length_y or 10))

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# 效果控制器与主程序
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
class BaseEffect:
    def __init__(self, canvas, width, height, config):
        self.canvas = canvas; self.width = width; self.height = height
        self.config = config; self.particles = []
    def update(self, global_wind):
        for p in self.particles: p.move(global_wind)
    def destroy(self):
        for p in self.particles: p.destroy()
        self.particles = []

class SnowEffect(BaseEffect):
    def __init__(self, canvas, width, height, config):
        super().__init__(canvas, width, height, config)
        for _ in range(self.config['num_snowflakes']):
            self.particles.append(Snowflake(canvas, width, height, config))

class RainEffect(BaseEffect):
    def __init__(self, canvas, width, height, config):
        super().__init__(canvas, width, height, config)
        for _ in range(self.config['num_raindrops']):
            self.particles.append(Raindrop(canvas, width, height, config))

class DesktopEffects:
    def __init__(self):
        self.config = {
            'num_snowflakes': 150,
            'snow_speed_range': (0.8, 2.0),
            'snow_sway_strength': 0.5,
            'num_raindrops': 300,
            'rain_speed_range': (10.0, 22.0),
            'global_wind_range': (-1.5, 1.5)
        }
        self.root = tk.Tk()
        self.screen_width = self.root.winfo_screenwidth(); self.screen_height = self.root.winfo_screenheight()
        self.global_wind = random.uniform(*self.config['global_wind_range'])
        self.config['global_wind'] = self.global_wind
        self.setup_window()
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height,
                                bg='#abcdef', highlightthickness=0)
        self.canvas.pack()
        self.current_effect_name = 'snow' # 默认启动雪花效果
        self.current_effect = None
        self.icon = None
        self.switch_effect(self.current_effect_name)
        self.is_running = True
        self.setup_tray_icon()
        self.update_animation()
        self.root.mainloop()

    def switch_effect(self, effect_name):
        if self.current_effect: self.current_effect.destroy()
        
        if effect_name == 'snow':
            self.current_effect = SnowEffect(self.canvas, self.screen_width, self.screen_height, self.config)
        elif effect_name == 'rain':
            self.current_effect = RainEffect(self.canvas, self.screen_width, self.screen_height, self.config)
        
        self.current_effect_name = effect_name
        
        if self.icon:
            self.icon.update_menu()
        
    def setup_window(self):
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.wm_attributes("-transparentcolor", '#abcdef')
        self.root.wm_attributes("-topmost", True)
        self.root.lift()

    def update_animation(self):
        if not self.is_running: return
        if random.random() < 0.002:
            self.global_wind = random.uniform(*self.config['global_wind_range'])
            self.config['global_wind'] = self.global_wind
        
        wind_for_effect = 0
        if self.current_effect_name == 'rain':
            wind_for_effect = self.global_wind

        if self.current_effect: self.current_effect.update(wind_for_effect)
        self.root.after(16, self.update_animation)

    def create_tray_image(self):
        width, height = 64, 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.ellipse((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill='lightblue')
        return image

    def quit_action(self, icon, item):
        self.is_running = False
        if self.icon:
            self.icon.stop()
        self.root.after(100, self.root.destroy)

    def setup_tray_icon(self):
        image = self.create_tray_image()

        def schedule_switch(effect_name):
            self.root.after(0, lambda: self.switch_effect(effect_name))

        menu = Menu(
            MenuItem('背景效果', Menu(
                MenuItem(
                    '雪花飘飘',
                    lambda: schedule_switch('snow'),
                    radio=True,
                    checked=lambda item: self.current_effect_name == 'snow'
                ),
                MenuItem(
                    '细雨纷纷',
                    lambda: schedule_switch('rain'),
                    radio=True,
                    checked=lambda item: self.current_effect_name == 'rain'
                )
            )),
            Menu.SEPARATOR,
            MenuItem('退出', self.quit_action)
        )
        self.icon = Icon("DesktopEffects", image, "桌面动态效果", menu)
        tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        tray_thread.start()

if __name__ == "__main__":
    app = DesktopEffects()
