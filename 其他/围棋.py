import tkinter as tk
from tkinter import messagebox, font, ttk
import copy
import math
import random
import threading
import time
import os
import subprocess
import json
from collections import deque

class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.last_board = None  # 用于检测劫的情况
        self.black_captures = 0
        self.white_captures = 0
        self.move_history = []  # 记录落子历史
        
    def place_stone(self, row, col, color):
        """尝试在指定位置放置棋子，返回是否成功放置"""
        # 检查位置是否为空
        if not (0 <= row < self.size and 0 <= col < self.size) or self.board[row][col] is not None:
            return False
            
        # 备份当前状态用于劫争检测
        old_board = copy.deepcopy(self.board)
        old_black_captures = self.black_captures
        old_white_captures = self.white_captures
            
        # 临时放置棋子
        self.board[row][col] = color
        
        # 检查并移除被吃掉的棋子
        captured = []
        for r, c in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
            if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == ('black' if color == 'white' else 'white'):
                group, liberties = self.find_group_and_liberties(r, c)
                if not liberties:
                    captured.extend(group)
        
        # 更新提子数量
        if color == 'black':
            self.black_captures += len(captured)
        else:
            self.white_captures += len(captured)
            
        # 执行提子
        for r, c in captured:
            self.board[r][c] = None
            
        # 如果没有吃子，检查自己的气
        if not captured:
            group, liberties = self.find_group_and_liberties(row, col)
            if not liberties:
                # 自杀规则，撤销落子
                self.board = old_board
                self.black_captures = old_black_captures
                self.white_captures = old_white_captures
                return False
                
        # 检查劫规则
        if self.last_board and self.board == self.last_board:
            # 违反劫规则，撤销落子
            self.board = old_board
            self.black_captures = old_black_captures
            self.white_captures = old_white_captures
            return False
            
        # 记录落子历史
        self.move_history.append((row, col, color))
        
        self.last_board = copy.deepcopy(old_board)
        return True
        
    def find_group_and_liberties(self, row, col):
        """查找与给定棋子相连的所有棋子（一个组）以及它们的气"""
        color = self.board[row][col]
        if color is None:
            return [], []
            
        visited = set()
        liberties = set()
        
        def dfs(r, c):
            if (r, c) in visited:
                return
                
            visited.add((r, c))
            
            for nr, nc in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.board[nr][nc] is None:
                        liberties.add((nr, nc))
                    elif self.board[nr][nc] == color:
                        dfs(nr, nc)
        
        dfs(row, col)
        return list(visited), list(liberties)
        
    def count_territory(self):
        """计算双方领地（粗略计算，不考虑死子）"""
        black_territory = 0
        white_territory = 0
        visited = set()
        
        for r in range(self.size):
            for c in range(self.size):
                if (r, c) in visited or self.board[r][c] is not None:
                    continue
                    
                territory = []
                is_black = True
                is_white = True
                
                def dfs(row, col):
                    if (row, col) in visited:
                        return
                        
                    visited.add((row, col))
                    if self.board[row][col] is None:
                        territory.append((row, col))
                        for nr, nc in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
                            if 0 <= nr < self.size and 0 <= nc < self.size:
                                dfs(nr, nc)
                    else:
                        nonlocal is_black, is_white
                        if self.board[row][col] == 'black':
                            is_white = False
                        else:
                            is_black = False
                
                dfs(r, c)
                
                if is_black and not is_white:
                    black_territory += len(territory)
                elif is_white and not is_black:
                    white_territory += len(territory)
                
        return black_territory, white_territory
        
    def estimate_winrate(self):
        """估算黑方胜率"""
        black_stones = sum(row.count('black') for row in self.board)
        white_stones = sum(row.count('white') for row in self.board)
        black_territory, white_territory = self.count_territory()
        
        black_score = black_stones + black_territory + self.black_captures
        white_score = white_stones + white_territory + self.white_captures + 6.5  # 贴目
        
        # 基于当前得分差距估算胜率
        score_diff = black_score - white_score
        winrate = 1 / (1 + math.exp(-score_diff / 10))  # 使用Sigmoid函数转换为0-1之间的概率
        return winrate * 100  # 转换为百分比

    def reset(self):
        """重置棋盘状态"""
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.last_board = None
        self.black_captures = 0
        self.white_captures = 0
        self.move_history = []
        
    def get_valid_moves(self, color):
        """获取所有合法落子点"""
        valid_moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] is None:
                    # 临时尝试放子
                    board_copy = copy.deepcopy(self.board)
                    black_captures_copy = self.black_captures
                    white_captures_copy = self.white_captures
                    last_board_copy = self.last_board
                    move_history_copy = self.move_history.copy()
                    
                    if self.place_stone(r, c, color):
                        valid_moves.append((r, c))
                        # 还原棋盘
                        self.board = board_copy
                        self.black_captures = black_captures_copy
                        self.white_captures = white_captures_copy
                        self.last_board = last_board_copy
                        self.move_history = move_history_copy
        
        return valid_moves
    
    def is_corner(self, row, col):
        """判断是否为角部"""
        corner_size = 3
        return ((row < corner_size or row >= self.size - corner_size) and 
                (col < corner_size or col >= self.size - corner_size))
    
    def is_edge(self, row, col):
        """判断是否为边缘"""
        edge_distance = 2
        return (row < edge_distance or row >= self.size - edge_distance or 
                col < edge_distance or col >= self.size - edge_distance)
    
    def is_center(self, row, col):
        """判断是否为中央区域"""
        center_start = self.size // 3
        center_end = self.size - center_start
        return (center_start <= row < center_end and center_start <= col < center_end)
    
    def evaluate_move_advanced(self, row, col, color, difficulty):
        """高级落子评估函数"""
        # 备份棋盘状态
        board_copy = copy.deepcopy(self.board)
        black_captures_copy = self.black_captures
        white_captures_copy = self.white_captures
        last_board_copy = self.last_board
        move_history_copy = self.move_history.copy()
        
        # 尝试落子
        if not self.place_stone(row, col, color):
            # 无效落子
            return float('-inf')
        
        score = 0
        
        # 1. 基础评分 - 所有难度级别都考虑
        # 1.1 吃子得分
        if color == 'black':
            captures = self.black_captures - black_captures_copy
        else:
            captures = self.white_captures - white_captures_copy
        score += captures * 15  # 提子权重高
        
        # 1.2 气数评估
        _, liberties = self.find_group_and_liberties(row, col)
        score += len(liberties) * 2  # 气越多越好
        
        # 1.3 避免在AI形成的大棋块周围填子（可能导致更多棋块被吃）
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == color:
                    group, group_libs = self.find_group_and_liberties(nr, nc)
                    if len(group) > 5 and len(group_libs) < 3:
                        score -= 10  # 大棋块气少，不要在周围填子
        
        # 中等及以上难度的评估
        if difficulty >= 1:
            # 2.1 位置评估
            center = self.size // 2
            distance_to_center = abs(row - center) + abs(col - center)
            
            # 开局偏好靠近中心
            early_game = len(self.move_history) < 30
            if early_game:
                score += (self.size - distance_to_center) * 0.5
            
            # 2.2 接近星位加分
            star_points = []
            if self.size == 19:
                star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
            elif self.size == 13:
                star_points = [(3, 3), (3, 9), (6, 6), (9, 3), (9, 9)]
            elif self.size == 9:
                star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
                
            for sr, sc in star_points:
                dist = abs(row - sr) + abs(col - sc)
                if dist <= 2:
                    score += 5 - dist  # 越近越好
            
            # 2.3 开局优先占角和边
            if len(self.move_history) < 15:
                if self.is_corner(row, col):
                    score += 8
                elif self.is_edge(row, col):
                    score += 5
            
            # 2.4 防守和进攻
            opponent_color = 'white' if color == 'black' else 'black'
            
            # 检查是否可以威胁对方的棋子
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == opponent_color:
                        opp_group, opp_libs = self.find_group_and_liberties(nr, nc)
                        if len(opp_libs) == 1:  # 对方只有一气
                            score += 12
                        elif len(opp_libs) == 2:  # 对方有两气
                            score += 8
        
        # 困难级别的评估
        if difficulty >= 2:
            # 3.1 形状评估 - 好的形状得分高
            # 检查是否形成好的形状（如虎口、金角银边等）
            adjacent_same_color = 0
            diagonal_same_color = 0
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.board[nr][nc] == color:
                        adjacent_same_color += 1
            
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    if self.board[nr][nc] == color:
                        diagonal_same_color += 1
            
            # 好的形状：有一定连接但不过密
            if adjacent_same_color == 1 and diagonal_same_color >= 1:
                score += 10  # 良好连接
            elif adjacent_same_color >= 3:
                score -= 5   # 过度拥挤
            
            # 3.2 领地控制
            # 模拟落子后的领地计算
            black_territory, white_territory = self.count_territory()
            if color == 'black':
                territory_diff = black_territory - white_territory
            else:
                territory_diff = white_territory - black_territory
            score += territory_diff * 0.8
            
            # 3.3 中盘策略 - 加强连接，保持灵活性
            mid_game = 30 <= len(self.move_history) < 150
            if mid_game:
                # 倾向于加强自己的连接
                for dr, dc in [(2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == color:
                        score += 3  # 强化连接
                
                # 倾向于在自己已有棋子的区域下棋（地域控制）
                own_stones_nearby = 0
                for r in range(max(0, row-3), min(self.size, row+4)):
                    for c in range(max(0, col-3), min(self.size, col+4)):
                        if self.board[r][c] == color:
                            own_stones_nearby += 1
                score += own_stones_nearby * 0.5
        
        # 恢复棋盘状态
        self.board = board_copy
        self.black_captures = black_captures_copy
        self.white_captures = white_captures_copy
        self.last_board = last_board_copy
        self.move_history = move_history_copy
        
        return score
        
    def ai_make_move(self, color, difficulty=1):
        """AI选择落子位置
        difficulty: 0-简单, 1-中等, 2-困难
        """
        valid_moves = self.get_valid_moves(color)
        if not valid_moves:
            return None  # 无处可下，选择跳过
        
        # 简单级别：更随机的选择
        if difficulty == 0:
            # 90%几率随机选择，10%几率使用评估
            if random.random() < 0.9:
                return random.choice(valid_moves)
        
        # 评估每个位置
        move_scores = {}
        for r, c in valid_moves:
            score = self.evaluate_move_advanced(r, c, color, difficulty)
            move_scores[(r, c)] = score
        
        # 按分数排序
        sorted_moves = sorted(move_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 根据难度级别选择前N个最佳选择中的一个
        if difficulty == 0:
            # 简单：从前50%的选择中随机选择
            top_n = max(1, len(sorted_moves) // 2)
            return random.choice(sorted_moves[:top_n])[0]
        elif difficulty == 1:
            # 中等：从前10个最佳选择中随机选择
            top_n = min(10, len(sorted_moves))
            choice_index = 0
            if top_n > 1:
                # 有80%的几率选择前3个最佳选择
                if random.random() < 0.8 and top_n >= 3:
                    choice_index = random.randint(0, 2)
                else:
                    choice_index = random.randint(0, top_n - 1)
            return sorted_moves[choice_index][0]
        else:
            # 困难：90%几率选择最佳选择，10%几率从前3个选择中随机选择
            if random.random() < 0.9 or len(sorted_moves) == 1:
                return sorted_moves[0][0]
            else:
                top_n = min(3, len(sorted_moves))
                return sorted_moves[random.randint(0, top_n - 1)][0]


class ExternalAI:
    """外部AI引擎接口（示例实现，实际使用需要安装相应软件）"""
    def __init__(self, engine_path=None):
        self.engine_path = engine_path
        self.process = None
        self.engine_type = None  # 'gnugo', 'katago', 等
        
    def initialize(self, engine_type='gnugo'):
        """初始化AI引擎"""
        self.engine_type = engine_type
        
        if engine_type == 'gnugo':
            # GNU Go的启动命令
            if self.engine_path:
                cmd = [self.engine_path, '--mode', 'gtp']
            else:
                cmd = ['gnugo', '--mode', 'gtp']  # 假设gnugo在PATH中
            
            try:
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                return True
            except Exception as e:
                print(f"启动GNU Go失败: {e}")
                return False
                
        elif engine_type == 'katago':
            # KataGo的启动命令（需要配置文件）
            if not self.engine_path:
                return False
                
            try:
                cmd = [self.engine_path, 'gtp', '-config', 'default_gtp.cfg']
                self.process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                return True
            except Exception as e:
                print(f"启动KataGo失败: {e}")
                return False
        
        return False
    
    def send_command(self, command):
        """向AI引擎发送GTP命令"""
        if not self.process:
            return None
            
        try:
            self.process.stdin.write(command + '\n')
            
            # 读取响应
            response = ""
            while True:
                line = self.process.stdout.readline()
                response += line
                if line.strip() == '':
                    break
            
            # 处理响应
            if response.startswith('='):
                return response[1:].strip()
            else:
                return None
        except Exception as e:
            print(f"与AI引擎通信失败: {e}")
            return None
    
    def get_move(self, board, color):
        """获取AI引擎推荐的落子位置"""
        if not self.process:
            return None
            
        # 清除棋盘并设置新局面
        self.send_command("clear_board")
        
        # 设置已有的棋子
        for r in range(board.size):
            for c in range(board.size):
                if board.board[r][c]:
                    stone_color = board.board[r][c]
                    vertex = self._coord_to_vertex(r, c)
                    self.send_command(f"play {stone_color} {vertex}")
        
        # 请求AI引擎计算下一步
        gtp_color = color
        response = self.send_command(f"genmove {gtp_color}")
        
        if response:
            # 解析落子位置
            vertex = response.strip()
            if vertex.lower() == 'pass':
                return None  # AI选择跳过
            else:
                row, col = self._vertex_to_coord(vertex)
                return (row, col)
        
        return None
    
    def _coord_to_vertex(self, row, col):
        """将坐标转换为GTP顶点表示法"""
        col_str = chr(col + ord('A') + (1 if col >= 8 else 0))  # GTP跳过'I'
        row_str = str(row + 1)
        return col_str + row_str
    
    def _vertex_to_coord(self, vertex):
        """将GTP顶点表示法转换为坐标"""
        col_str = vertex[0].upper()
        row_str = vertex[1:]
        
        col = ord(col_str) - ord('A')
        if col_str >= 'J':  # GTP跳过'I'
            col -= 1
        row = int(row_str) - 1
        
        return row, col
    
    def close(self):
        """关闭AI引擎"""
        if self.process:
            try:
                self.send_command("quit")
                self.process.terminate()
                self.process = None
            except:
                pass


class GoGame:
    def __init__(self, master, size=19):
        self.master = master
        self.size = size
        self.board = GoBoard(size)
        self.current_player = 'black'  # 黑方先手
        self.passed_last_turn = False
        self.ai_enabled = False
        self.ai_color = 'white'  # AI默认执白
        self.ai_thinking = False
        self.ai_difficulty = 1  # 默认中等难度
        self.external_ai = None
        self.use_external_ai = False
        
        # 设置更大的字体
        self.large_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.normal_font = font.Font(family="Helvetica", size=12)
        
        # 创建GUI
        self.canvas_size = min(800, 30 * size)
        self.cell_size = self.canvas_size / (size + 1)
        
        # 顶部菜单栏
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)
        
        # 游戏菜单
        self.game_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="游戏", menu=self.game_menu)
        self.game_menu.add_command(label="新游戏", command=self.restart_game)
        self.game_menu.add_separator()
        self.game_menu.add_command(label="退出", command=master.quit)
        
        # 设置菜单
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="设置", menu=self.settings_menu)
        self.settings_menu.add_command(label="棋盘大小", command=self.change_board_size)
        
        # 创建主框架
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        self.control_frame = tk.Frame(self.main_frame, width=200)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # AI设置框架
        self.ai_frame = tk.LabelFrame(self.control_frame, text="AI设置", font=self.normal_font)
        self.ai_frame.pack(fill=tk.X, pady=5)
        
        self.ai_var = tk.BooleanVar(value=False)
        self.ai_check = tk.Checkbutton(self.ai_frame, text="启用AI对手", 
                                       variable=self.ai_var, 
                                       command=self.toggle_ai,
                                       font=self.normal_font)
        self.ai_check.pack(fill=tk.X, padx=10, pady=5)
        
        # AI颜色选择
        self.ai_color_frame = tk.Frame(self.ai_frame)
        self.ai_color_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.ai_color_var = tk.StringVar(value="white")
        self.ai_black = tk.Radiobutton(self.ai_color_frame, text="AI执黑", 
                                      variable=self.ai_color_var, 
                                      value="black",
                                      command=self.set_ai_color,
                                      font=self.normal_font)
        self.ai_white = tk.Radiobutton(self.ai_color_frame, text="AI执白", 
                                      variable=self.ai_color_var, 
                                      value="white",
                                      command=self.set_ai_color,
                                      font=self.normal_font)
        self.ai_black.pack(side=tk.LEFT)
        self.ai_white.pack(side=tk.LEFT)
        
        # AI难度选择
        self.ai_difficulty_frame = tk.Frame(self.ai_frame)
        self.ai_difficulty_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(self.ai_difficulty_frame, text="AI难度:", font=self.normal_font).pack(side=tk.LEFT)
        
        self.ai_difficulty_var = tk.IntVar(value=1)
        self.ai_difficulty_combo = ttk.Combobox(self.ai_difficulty_frame, 
                                               textvariable=self.ai_difficulty_var,
                                               values=["简单", "中等", "困难", "专家(外部引擎)"],
                                               state="readonly",
                                               width=12)
        self.ai_difficulty_combo.current(1)  # 默认选择中等难度
        self.ai_difficulty_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.ai_difficulty_combo.bind("<<ComboboxSelected>>", self.set_ai_difficulty)
        
        # 外部AI引擎设置
        self.external_ai_frame = tk.Frame(self.ai_frame)
        self.external_ai_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.external_ai_button = tk.Button(self.external_ai_frame, 
                                          text="配置外部AI引擎", 
                                          command=self.configure_external_ai,
                                          font=self.normal_font)
        self.external_ai_button.pack(fill=tk.X)
        
        # 按钮框架
        self.button_frame = tk.LabelFrame(self.control_frame, text="游戏控制", font=self.normal_font)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        self.pass_button = tk.Button(self.button_frame, text="跳过", 
                                    command=self.pass_turn, 
                                    font=self.large_font,
                                    padx=10, pady=5)
        self.pass_button.pack(fill=tk.X, padx=10, pady=5)
        
        self.resign_button = tk.Button(self.button_frame, text="认输", 
                                      command=self.resign, 
                                      font=self.large_font,
                                      padx=10, pady=5)
        self.resign_button.pack(fill=tk.X, padx=10, pady=5)
        
        self.restart_button = tk.Button(self.button_frame, text="重新开始", 
                                       command=self.restart_game, 
                                       font=self.large_font,
                                       padx=10, pady=5)
        self.restart_button.pack(fill=tk.X, padx=10, pady=5)
        
        # 游戏信息框架
        self.info_frame = tk.LabelFrame(self.control_frame, text="游戏信息", font=self.normal_font)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.turn_var = tk.StringVar(value="当前玩家: 黑方")
        self.turn_label = tk.Label(self.info_frame, textvariable=self.turn_var, font=self.normal_font)
        self.turn_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.captures_var = tk.StringVar(value="提子 - 黑方: 0, 白方: 0")
        self.captures_label = tk.Label(self.info_frame, textvariable=self.captures_var, font=self.normal_font)
        self.captures_label.pack(fill=tk.X, padx=10, pady=5)
        
        # 胜率显示框架
        self.winrate_frame = tk.Frame(self.info_frame)
        self.winrate_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.black_winrate_var = tk.StringVar(value="黑方胜率: 50.0%")
        self.black_winrate_label = tk.Label(self.winrate_frame, textvariable=self.black_winrate_var, font=self.normal_font, fg="black")
        self.black_winrate_label.pack(side=tk.LEFT)
        
        self.white_winrate_var = tk.StringVar(value="白方胜率: 50.0%")
        self.white_winrate_label = tk.Label(self.winrate_frame, textvariable=self.white_winrate_var, font=self.normal_font, fg="blue")
        self.white_winrate_label.pack(side=tk.RIGHT)
        
        # 右侧棋盘区域
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.board_frame, width=self.canvas_size, height=self.canvas_size, bg='#DDBB88')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_frame = tk.Frame(master)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var, font=self.normal_font)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 初始化棋盘并绑定事件
        self.draw_board()
        self.canvas.bind("<Button-1>", self.handle_click)
        
    def change_board_size(self):
        """修改棋盘大小"""
        sizes = [9, 13, 19]
        dialog = tk.Toplevel(self.master)
        dialog.title("选择棋盘大小")
        dialog.geometry("250x150")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        tk.Label(dialog, text="选择棋盘大小:", font=self.normal_font).pack(pady=10)
        
        size_var = tk.IntVar(value=self.size)
        for size in sizes:
            tk.Radiobutton(dialog, text=f"{size}×{size}", variable=size_var, value=size, font=self.normal_font).pack(anchor=tk.W, padx=20)
        
        def apply_size():
            new_size = size_var.get()
            if new_size != self.size:
                self.size = new_size
                self.board = GoBoard(new_size)
                self.cell_size = self.canvas_size / (new_size + 1)
                self.reset_game()
            dialog.destroy()
        
        tk.Button(dialog, text="确定", command=apply_size, font=self.normal_font).pack(pady=10)
        
        # 居中显示对话框
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def toggle_ai(self):
        """启用或禁用AI"""
        self.ai_enabled = self.ai_var.get()
        
        # 如果选择了专家级别（外部引擎）但未配置
        if self.ai_enabled and self.ai_difficulty_var.get() == 3 and not self.use_external_ai:
            self.configure_external_ai()
            
        if self.ai_enabled and self.current_player == self.ai_color:
            self.make_ai_move()
            
    def set_ai_color(self):
        """设置AI执黑或执白"""
        self.ai_color = self.ai_color_var.get()
        # 如果当前轮到AI，立即行动
        if self.ai_enabled and self.current_player == self.ai_color:
            self.make_ai_move()
            
    def set_ai_difficulty(self, event=None):
        """设置AI难度"""
        self.ai_difficulty = self.ai_difficulty_var.get()
        
        # 如果选择了专家级别（外部引擎）
        if self.ai_difficulty == 3:
            if not self.use_external_ai:
                self.configure_external_ai()
        else:
            self.use_external_ai = False
            
        # 如果AI已启用且轮到AI行动，使用新难度级别
        if self.ai_enabled and self.current_player == self.ai_color:
            self.make_ai_move()
            
    def configure_external_ai(self):
        """配置外部AI引擎"""
        dialog = tk.Toplevel(self.master)
        dialog.title("配置外部AI引擎")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        tk.Label(dialog, text="外部AI引擎设置", font=self.large_font).pack(pady=10)
        
        # 引擎类型选择
        engine_frame = tk.Frame(dialog)
        engine_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(engine_frame, text="引擎类型:", font=self.normal_font).pack(side=tk.LEFT)
        
        engine_var = tk.StringVar(value="gnugo")
        engine_combo = ttk.Combobox(engine_frame, 
                                  textvariable=engine_var,
                                  values=["GNU Go", "KataGo"],
                                  state="readonly",
                                  width=10)
        engine_combo.current(0)
        engine_combo.pack(side=tk.LEFT, padx=5)
        
        # 路径设置
        path_frame = tk.Frame(dialog)
        path_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(path_frame, text="引擎路径:", font=self.normal_font).pack(side=tk.LEFT)
        
        path_var = tk.StringVar()
        path_entry = tk.Entry(path_frame, textvariable=path_var, width=30)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        # 浏览按钮
        def browse_engine():
            file_path = tk.filedialog.askopenfilename(
                title="选择AI引擎可执行文件",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if file_path:
                path_var.set(file_path)
                
        browse_button = tk.Button(path_frame, text="浏览...", command=browse_engine)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # 说明文本
        info_text = "注意：\n"
        info_text += "1. 使用外部AI引擎需要预先安装相应软件\n"
        info_text += "2. GNU Go是一个开源围棋程序，强度适中\n"
        info_text += "3. KataGo是一个先进的围棋AI，需要额外配置\n"
        info_text += "4. 如果路径留空，将尝试使用系统PATH中的程序"
        
        info_label = tk.Label(dialog, text=info_text, font=self.normal_font, justify=tk.LEFT)
        info_label.pack(padx=20, pady=10, anchor=tk.W)
        
        # 测试连接按钮
        def test_connection():
            engine_path = path_var.get() if path_var.get() else None
            engine_type = "gnugo" if engine_var.get() == "GNU Go" else "katago"
            
            test_ai = ExternalAI(engine_path)
            if test_ai.initialize(engine_type):
                test_ai.close()
                tk.messagebox.showinfo("测试成功", "成功连接到AI引擎！")
            else:
                tk.messagebox.showerror("测试失败", "无法连接到AI引擎，请检查路径和安装情况。")
        
        test_button = tk.Button(dialog, text="测试连接", command=test_connection, font=self.normal_font)
        test_button.pack(pady=5)
        
        # 确定按钮
        def apply_settings():
            engine_path = path_var.get() if path_var.get() else None
            engine_type = "gnugo" if engine_var.get() == "GNU Go" else "katago"
            
            # 尝试初始化外部AI
            if self.external_ai:
                self.external_ai.close()
                
            self.external_ai = ExternalAI(engine_path)
            if self.external_ai.initialize(engine_type):
                self.use_external_ai = True
                tk.messagebox.showinfo("设置成功", f"已成功配置{engine_var.get()}引擎。")
                dialog.destroy()
            else:
                self.external_ai = None
                self.use_external_ai = False
                tk.messagebox.showerror("设置失败", "无法初始化AI引擎，请检查设置。")
        
        apply_button = tk.Button(dialog, text="确定", command=apply_settings, font=self.normal_font)
        apply_button.pack(pady=10)
        
        # 居中显示对话框
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def draw_board(self):
        """绘制棋盘"""
        self.canvas.delete("all")
        
        # 绘制棋盘背景和网格
        margin = self.cell_size
        for i in range(self.size):
            # 横线
            self.canvas.create_line(
                margin, margin + i * self.cell_size,
                self.canvas_size - margin, margin + i * self.cell_size,
                width=1
            )
            # 竖线
            self.canvas.create_line(
                margin + i * self.cell_size, margin,
                margin + i * self.cell_size, self.canvas_size - margin,
                width=1
            )
        
        # 绘制星位
        star_points = []
        if self.size == 19:
            star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        elif self.size == 13:
            star_points = [(3, 3), (3, 9), (6, 6), (9, 3), (9, 9)]
        elif self.size == 9:
            star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
            
        for row, col in star_points:
            x = margin + col * self.cell_size
            y = margin + row * self.cell_size
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill='black')
        
        # 绘制棋子
        for row in range(self.size):
            for col in range(self.size):
                if self.board.board[row][col]:
                    x = margin + col * self.cell_size
                    y = margin + row * self.cell_size
                    color = self.board.board[row][col]
                    
                    # 绘制棋子阴影
                    self.canvas.create_oval(
                        x - self.cell_size/2.5 + 2, y - self.cell_size/2.5 + 2,
                        x + self.cell_size/2.5 + 2, y + self.cell_size/2.5 + 2,
                        fill="#aaaaaa", outline=""
                    )
                    
                    # 绘制棋子
                    self.canvas.create_oval(
                        x - self.cell_size/2.5, y - self.cell_size/2.5,
                        x + self.cell_size/2.5, y + self.cell_size/2.5,
                        fill=color, outline="black" if color == "white" else ""
                    )
                    
                    # 如果是最后一手棋，标记它
                    if len(self.board.move_history) > 0:
                        last_row, last_col, _ = self.board.move_history[-1]
                        if row == last_row and col == last_col:
                            mark_color = "black" if color == "white" else "white"
                            self.canvas.create_oval(
                                x - self.cell_size/8, y - self.cell_size/8,
                                x + self.cell_size/8, y + self.cell_size/8,
                                fill=mark_color, outline=""
                            )
    
    def handle_click(self, event):
        """处理鼠标点击事件"""
        # 如果AI正在思考或当前玩家是AI，忽略点击
        if self.ai_thinking or (self.ai_enabled and self.current_player == self.ai_color):
            return
            
        margin = self.cell_size
        # 计算最近的交叉点
        col = round((event.x - margin) / self.cell_size)
        row = round((event.y - margin) / self.cell_size)
        
        if 0 <= row < self.size and 0 <= col < self.size:
            # 尝试放置棋子
            if self.board.place_stone(row, col, self.current_player):
                self.after_move()
    
    def after_move(self):
        """落子后的处理"""
        # 切换玩家
        self.current_player = 'white' if self.current_player == 'black' else 'black'
        self.passed_last_turn = False
        
        # 更新显示
        self.turn_var.set(f"当前玩家: {'黑方' if self.current_player == 'black' else '白方'}")
        self.captures_var.set(f"提子 - 黑方: {self.board.black_captures}, 白方: {self.board.white_captures}")
        
        # 更新胜率
        self.update_winrate()
        
        # 更新棋盘
        self.draw_board()
        
        # 如果轮到AI，让AI行动
        if self.ai_enabled and self.current_player == self.ai_color:
            self.make_ai_move()
    
    def make_ai_move(self):
        """让AI落子"""
        if self.ai_thinking:
            return
            
        self.ai_thinking = True
        difficulty_names = ["简单", "中等", "困难", "专家"]
        self.status_var.set(f"{difficulty_names[self.ai_difficulty]}级AI正在思考...")
        self.master.update()
        
        # 在单独的线程中运行AI，避免UI卡顿
        def ai_thread():
            time.sleep(0.5)  # 稍作延迟，让用户看到AI在"思考"
            
            if self.use_external_ai and self.external_ai:
                # 使用外部AI引擎
                move = self.external_ai.get_move(self.board, self.current_player)
            else:
                # 使用内置AI
                move = self.board.ai_make_move(self.current_player, self.ai_difficulty)
            
            # 在主线程中更新UI
            self.master.after(0, lambda: self.complete_ai_move(move))
        
        threading.Thread(target=ai_thread).start()
    
    def complete_ai_move(self, move):
        """完成AI的落子"""
        self.ai_thinking = False
        self.status_var.set("")
        
        if move is None:
            # AI选择跳过
            self.pass_turn()
        else:
            row, col = move
            if self.board.place_stone(row, col, self.current_player):
                self.after_move()
    
    def update_winrate(self):
        """更新胜率显示"""
        black_winrate = self.board.estimate_winrate()
        white_winrate = 100 - black_winrate
        
        self.black_winrate_var.set(f"黑方胜率: {black_winrate:.1f}%")
        self.white_winrate_var.set(f"白方胜率: {white_winrate:.1f}%")
    
    def pass_turn(self):
        """跳过当前回合"""
        # 如果AI正在思考，忽略
        if self.ai_thinking:
            return
            
        # 如果双方连续PASS，游戏结束
        if self.passed_last_turn:
            self.end_game()
        else:
            self.passed_last_turn = True
            self.current_player = 'white' if self.current_player == 'black' else 'black'
            self.turn_var.set(f"当前玩家: {'黑方' if self.current_player == 'black' else '白方'}")
            
            # 更新胜率
            self.update_winrate()
            
            # 如果轮到AI，让AI行动
            if self.ai_enabled and self.current_player == self.ai_color:
                self.make_ai_move()
    
    def resign(self):
        """认输"""
        # 如果AI正在思考，忽略
        if self.ai_thinking:
            return
            
        winner = '黑方' if self.current_player == 'white' else '白方'
        messagebox.showinfo("游戏结束", f"{winner}获胜！(认输)")
        
        # 清空棋盘并重置游戏
        self.reset_game()
    
    def restart_game(self):
        """重新开始游戏"""
        # 如果AI正在思考，忽略
        if self.ai_thinking:
            return
            
        if messagebox.askyesno("重新开始", "确定要重新开始游戏吗？"):
            self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        self.board.reset()
        self.current_player = 'black'
        self.passed_last_turn = False
        self.turn_var.set("当前玩家: 黑方")
        self.captures_var.set("提子 - 黑方: 0, 白方: 0")
        self.black_winrate_var.set("黑方胜率: 50.0%")
        self.white_winrate_var.set("白方胜率: 50.0%")
        self.status_var.set("")
        self.draw_board()
        
        # 如果启用了AI且AI执黑，让AI行动
        if self.ai_enabled and self.ai_color == 'black':
            self.make_ai_move()
    
    def end_game(self):
        """结束游戏，计算得分"""
        black_territory, white_territory = self.board.count_territory()
        black_stones = sum(row.count('black') for row in self.board.board)
        white_stones = sum(row.count('white') for row in self.board.board)
        
        black_score = black_territory + self.board.black_captures
        white_score = white_territory + self.board.white_captures + 6.5  # 贴目
        
        result = f"游戏结束！\n\n黑方:\n - 领地: {black_territory} 目\n - 提子: {self.board.black_captures} 子\n - 总计: {black_score} 目\n\n"
        result += f"白方:\n - 领地: {white_territory} 目\n - 提子: {self.board.white_captures} 子\n - 贴目: 6.5 目\n - 总计: {white_score} 目\n\n"
        
        if black_score > white_score:
            result += f"黑方胜 {black_score - white_score:.1f} 目！"
        else:
            result += f"白方胜 {white_score - black_score:.1f} 目！"
            
        messagebox.showinfo("游戏结果", result)
        
        # 游戏结束后重置棋盘
        self.reset_game()
        
    def __del__(self):
        """析构函数，确保关闭外部AI引擎"""
        if self.external_ai:
            self.external_ai.close()

def main():
    root = tk.Tk()
    root.title("围棋")
    # 设置窗口图标（如果有）
    #root.iconbitmap("go_icon.ico")  # 取消注释并提供图标路径
    
    # 设置窗口大小和位置
    window_width = 1000
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    game = GoGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()