import pygame
import sys
import random
import os
from collections import deque

# 初始化 Pygame
pygame.init()

# 屏幕尺寸
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("随机迷宫游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

# 音乐和音效
music_volume = 0.5
sound_volume = 0.5

# 背景音乐 - 随机选择
piano_songs = [
    'sound/piano1.wav',  # 替换为 Pygame 自带的音乐文件路径
    'sound/piano2.wav',
    'sound/piano3.wav'
]

# 检查并加载背景音乐
background_music_path = random.choice(piano_songs)
if os.path.exists(background_music_path):
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(music_volume)
else:
    print(f"背景音乐文件 '{background_music_path}' 未找到，跳过设置背景音乐。")

# 加载音效
click_sound_path = 'sound/water_drop.wav'  # 使用 pygame 自带的音效路径
if os.path.exists(click_sound_path):
    click_sound = pygame.mixer.Sound(click_sound_path)
    click_sound.set_volume(sound_volume)
else:
    print(f"音效文件 '{click_sound_path}' 未找到，跳过加载音效。")
    click_sound = None  # 如果音效文件不存在，设置为 None

# 加载支持汉字的字体（使用指定的字体路径）
font_path = 'C:\\Windows\\Fonts\\STXINWEI.TTF'  # 这里使用华文新魏字体

# 定义迷宫参数
CELL_SIZE = 40
cols = WIDTH // CELL_SIZE
rows = HEIGHT // CELL_SIZE

# 迷宫生成算法使用的栈
stack = []

# 定义 Cell 类
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = [True, True, True, True]  # 上右下左
        self.visited = False

    def draw(self):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE

        if self.visited:
            pygame.draw.rect(screen, WHITE, (x, y, CELL_SIZE, CELL_SIZE))

        if self.walls[0]:
            pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y))
        if self.walls[1]:
            pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE))
        if self.walls[2]:
            pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y + CELL_SIZE), (x, y + CELL_SIZE))
        if self.walls[3]:
            pygame.draw.line(screen, BLACK, (x, y + CELL_SIZE), (x, y))

    def highlight(self, color):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

def index(x, y):
    if x < 0 or y < 0 or x > cols - 1 or y > rows -1:
        return None
    return grid[y][x]

def remove_walls(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    if dx == 1:
        a.walls[3] = False  # 移除左墙
        b.walls[1] = False  # 移除右墙
    elif dx == -1:
        a.walls[1] = False  # 移除右墙
        b.walls[3] = False  # 移除左墙
    if dy == 1:
        a.walls[0] = False  # 移除上墙
        b.walls[2] = False  # 移除下墙
    elif dy == -1:
        a.walls[2] = False  # 移除下墙
        b.walls[0] = False  # 移除上墙

# 生成迷宫
def generate_maze():
    global current
    current.visited = True
    next_cell = get_next_cell(current)
    if next_cell:
        next_cell.visited = True
        stack.append(current)
        remove_walls(current, next_cell)
        current = next_cell
    elif stack:
        current = stack.pop()

def get_next_cell(cell):
    neighbors = []
    directions = [
        (0, -1),  # 上
        (1, 0),   # 右
        (0, 1),   # 下
        (-1, 0)   # 左
    ]
    for dx, dy in directions:
        neighbor = index(cell.x + dx, cell.y + dy)
        if neighbor and not neighbor.visited:
            neighbors.append(neighbor)
    if neighbors:
        return random.choice(neighbors)
    else:
        return None

# 创建迷宫网格
grid = []
for y in range(rows):
    grid.append([])
    for x in range(cols):
        grid[y].append(Cell(x, y))

current = grid[0][0]

# 玩家
player_x, player_y = 0, rows - 1  # 左下角
player_pos = [player_x * CELL_SIZE + CELL_SIZE // 2, player_y * CELL_SIZE + CELL_SIZE // 2]
player_color = BLUE

# 出口
exit_x, exit_y = cols - 1, 0  # 右上角

# 游戏状态
game_state = 'menu'

# 主菜单函数
def main_menu():
    font = pygame.font.Font(font_path, 74)  # 使用支持汉字的字体
    while True:
        screen.fill(YELLOW)
        title_text = font.render("迷宫游戏", True, RED)
        start_text = font.render("开始游戏", True, GREEN)
        settings_text = font.render("设置", True, GREEN)
        quit_text = font.render("退出游戏", True, GREEN)

        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 200))
        screen.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, 300))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if click_sound:  # 只有在音效文件成功加载时才播放音效
                    click_sound.play()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 200 <= mouse_y <= 200 + start_text.get_height():
                    return 'game'
                if 300 <= mouse_y <= 300 + settings_text.get_height():
                    settings_menu()
                if 400 <= mouse_y <= 400 + quit_text.get_height():
                    pygame.quit()
                    sys.exit()

# 设置菜单函数
def settings_menu():
    global music_volume, sound_volume
    font = pygame.font.Font(font_path, 50)  # 使用支持汉字的字体

    # 滑动条位置和尺寸
    slider_x = WIDTH // 2 - 100
    music_slider_y = 200
    sound_slider_y = 300
    slider_width = 200
    slider_height = 10
    handle_width = 20
    handle_height = 30

    dragging_music = False  # 是否在拖动音乐滑块
    dragging_sound = False  # 是否在拖动音效滑块

    while True:
        screen.fill(YELLOW)
        
        # 绘制文本
        music_text = font.render(f"音乐音量: {int(music_volume * 100)}%", True, BLACK)
        sound_text = font.render(f"音效音量: {int(sound_volume * 100)}%", True, BLACK)
        back_text = font.render("返回", True, GREEN)

        screen.blit(music_text, (WIDTH // 2 - music_text.get_width() // 2, music_slider_y - 50))
        screen.blit(sound_text, (WIDTH // 2 - sound_text.get_width() // 2, sound_slider_y - 50))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, 400))

        # 绘制滑动条背景
        pygame.draw.rect(screen, GRAY, (slider_x, music_slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, GRAY, (slider_x, sound_slider_y, slider_width, slider_height))

        # 绘制滑块
        music_handle_x = slider_x + int(music_volume * slider_width) - handle_width // 2
        sound_handle_x = slider_x + int(sound_volume * slider_width) - handle_width // 2
        pygame.draw.rect(screen, GREEN, (music_handle_x, music_slider_y - (handle_height - slider_height) // 2, handle_width, handle_height))
        pygame.draw.rect(screen, GREEN, (sound_handle_x, sound_slider_y - (handle_height - slider_height) // 2, handle_width, handle_height))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if click_sound:  # 只有在音效文件成功加载时才播放音效
                    click_sound.play()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # 判断是否点击到音乐音量滑块
                if music_handle_x <= mouse_x <= music_handle_x + handle_width and music_slider_y - (handle_height - slider_height) // 2 <= mouse_y <= music_slider_y + handle_height:
                    dragging_music = True
                # 判断是否点击到音效音量滑块
                elif sound_handle_x <= mouse_x <= sound_handle_x + handle_width and sound_slider_y - (handle_height - slider_height) // 2 <= mouse_y <= sound_slider_y + handle_height:
                    dragging_sound = True
                # 判断是否点击返回按钮
                elif 400 <= mouse_y <= 400 + back_text.get_height() and WIDTH // 2 - back_text.get_width() // 2 <= mouse_x <= WIDTH // 2 + back_text.get_width() // 2:
                    return
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # 结束拖动
                dragging_music = False
                dragging_sound = False
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # 拖动音乐音量滑块
                if dragging_music:
                    new_volume = (mouse_x - slider_x) / slider_width
                    music_volume = max(0, min(new_volume, 1))  # 限制在0到1之间
                    pygame.mixer.music.set_volume(music_volume)
                # 拖动音效音量滑块
                elif dragging_sound:
                    new_volume = (mouse_x - slider_x) / slider_width
                    sound_volume = max(0, min(new_volume, 1))  # 限制在0到1之间
                    if click_sound:
                        click_sound.set_volume(sound_volume)

# 恭喜界面
def congrats_screen():
    font = pygame.font.Font(font_path, 74)
    while True:
        screen.fill(YELLOW)
        congrats_text = font.render("恭喜通关!", True, RED)
        back_text = font.render("返回主菜单", True, GREEN)

        screen.blit(congrats_text, (WIDTH//2 - congrats_text.get_width()//2, 200))
        screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, 300))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                click_sound.play()  # 播放点击音效
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if 300 <= mouse_y <= 300 + back_text.get_height():
                    return 'menu'

# 寻找从当前位置到出口的最短路径（BFS）
def find_shortest_path(start_x, start_y, end_x, end_y):
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    queue = deque()
    queue.append((start_x, start_y, []))
    visited[start_y][start_x] = True

    while queue:
        x, y, path = queue.popleft()
        cell = grid[y][x]
        if x == end_x and y == end_y:
            return path
        directions = [
            (0, -1, 0),  # 上
            (1, 0, 1),   # 右
            (0, 1, 2),   # 下
            (-1, 0, 3)   # 左
        ]
        for dx, dy, wall in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                neighbor = grid[ny][nx]
                if not visited[ny][nx]:
                    if not cell.walls[wall]:
                        visited[ny][nx] = True
                        queue.append((nx, ny, path + [(nx, ny)]))
    return []

# 绘制进度条
def draw_progress_bar(distance, max_distance):
    # 计算进度条的高度比例
    progress_height = HEIGHT * (1 - distance / max_distance)
    pygame.draw.rect(screen, GRAY, (WIDTH - 20, 0, 20, HEIGHT))  # 背景条
    pygame.draw.rect(screen, GREEN, (WIDTH - 20, HEIGHT - progress_height, 20, progress_height))  # 动态条

# 计算玩家到出口的距离
def calculate_distance(player_x, player_y, exit_x, exit_y):
    return abs(player_x - exit_x) + abs(player_y - exit_y)

# 主游戏循环
while True:
    if game_state == 'menu':
        game_state = main_menu()
        # 重置迷宫和玩家位置
        grid = []
        for y in range(rows):
            grid.append([])
            for x in range(cols):
                grid[y].append(Cell(x, y))
        current = grid[0][0]
        player_x, player_y = 0, rows - 1  # 左下角
        player_pos = [player_x * CELL_SIZE + CELL_SIZE // 2, player_y * CELL_SIZE + CELL_SIZE // 2]
    elif game_state == 'game':
        screen.fill(BLACK)

        # 生成迷宫
        while True:
            generate_maze()
            if all(cell.visited for row in grid for cell in row):
                break

        # 游戏主循环
        running = True
        auto_move = False  # 是否自动移动
        path = []  # 自动移动的路径
        path_index = 0  # 路径中的当前索引

        while running:
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # 检查是否按下回车或空格键，启动自动移动
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        auto_move = True
                        path = find_shortest_path(player_x, player_y, exit_x, exit_y)
                        path_index = 0
                elif event.type == pygame.KEYUP:
                    # 松开回车或空格键，停止自动移动
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        auto_move = False

            if auto_move and path:
                # 自动移动
                if path_index < len(path):
                    player_x, player_y = path[path_index]
                    path_index += 1
                else:
                    auto_move = False  # 到达路径终点，停止自动移动
            else:
                # 手动移动
                keys = pygame.key.get_pressed()  # 获取按键状态
                cell = grid[player_y][player_x]
                if keys[pygame.K_LEFT] and player_x > 0 and not cell.walls[3]:
                    player_x -= 1
                if keys[pygame.K_RIGHT] and player_x < cols - 1 and not cell.walls[1]:
                    player_x += 1
                if keys[pygame.K_UP] and player_y > 0 and not cell.walls[0]:
                    player_y -= 1
                if keys[pygame.K_DOWN] and player_y < rows - 1 and not cell.walls[2]:
                    player_y += 1

            player_pos = [player_x * CELL_SIZE + CELL_SIZE // 2, player_y * CELL_SIZE + CELL_SIZE // 2]

            # 绘制迷宫
            for row in grid:
                for cell in row:
                    cell.draw()

            # 绘制玩家
            pygame.draw.circle(screen, player_color, player_pos, CELL_SIZE // 2 - 2)

            # 绘制出口
            pygame.draw.rect(screen, RED, (exit_x * CELL_SIZE, exit_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # 绘制进度条
            distance = calculate_distance(player_x, player_y, exit_x, exit_y)
            draw_progress_bar(distance, rows + cols - 2)

            pygame.display.flip()

            # 检查是否到达出口
            if player_x == exit_x and player_y == exit_y:
                game_state = congrats_screen()
                running = False
    else:
        pygame.quit()
        sys.exit()
