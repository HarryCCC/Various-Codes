import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

# 定义迷宫环境
class MazeEnv:
    def __init__(self):
        # 0表示空地，-1表示障碍
        self.maze = np.array([
            [0, 0, 0, 0, 0],
            [0, -1, -1, -1, 0],
            [0, 0, 0, -1, 0],
            [0, -1, 0, 0, 0],
            [0, 0, 0, -1, 0]
        ])
        self.start_pos = (0, 0)  # 起点
        self.goal_pos = (4, 4)   # 终点
        self.reset()
            
    def reset(self):
        self.position = self.start_pos
        return self.position
        
    def step(self, action):
        x, y = self.position
        if action == 0:   # 上
            x -= 1
        elif action == 1: # 下
            x += 1
        elif action == 2: # 左
            y -= 1
        elif action == 3: # 右
            y += 1
            
        # 检查是否撞墙或越界
        if x < 0 or x >= self.maze.shape[0] or y < 0 or y >= self.maze.shape[1] or self.maze[x, y] == -1:
            x, y = self.position  # 保持原地不动
            
        self.position = (x, y)
            
        # 判断是否到达终点
        if self.position == self.goal_pos:
            reward = 1
            done = True
        else:
            reward = -0.01  # 每一步都有微小的惩罚
            done = False
            
        return self.position, reward, done
        
    def render(self, path=[], episode=0):
        maze_render = self.maze.copy()
        
        # 创建颜色映射
        cmap = colors.ListedColormap(['white', 'black', 'green', 'red', 'yellow'])
        bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
        norm = colors.BoundaryNorm(bounds, cmap.N)
        
        # 标记起点和终点
        maze_render[self.start_pos] = 2  # 起点为绿色
        maze_render[self.goal_pos] = 3   # 终点为红色
        
        fig, ax = plt.subplots()
        ax.imshow(maze_render, cmap=cmap, norm=norm)
        
        # 在迷宫上绘制路径，使用数字标注步数
        for idx, pos in enumerate(path):
            if pos != self.start_pos and pos != self.goal_pos:
                ax.text(pos[1], pos[0], str(idx), va='center', ha='center', color='blue')
        
        ax.set_title(f'Episode {episode}: Path Length = {len(path)}')
        plt.axis('off')
        plt.show()

# 定义Q-learning算法
env = MazeEnv()
q_table = np.zeros((env.maze.shape[0], env.maze.shape[1], 4))  # 四个动作

# 超参数
alpha = 0.1    # 学习率
gamma = 0.9    # 折扣因子
epsilon = 0.1  # 探索率
num_episodes = 100

# 记录每个回合的路径长度
path_lengths = []

for episode in range(num_episodes):
    state = env.reset()
    done = False
    path = [state]
        
    while not done:
        x, y = state
            
        # ε-贪心策略选择动作
        if np.random.rand() < epsilon:
            action = np.random.choice(4)
        else:
            action = np.argmax(q_table[x, y, :])
            
        next_state, reward, done = env.step(action)
        nx, ny = next_state
            
        # 更新Q值
        q_predict = q_table[x, y, action]
        if done:
            q_target = reward
        else:
            q_target = reward + gamma * np.max(q_table[nx, ny, :])
        q_table[x, y, action] += alpha * (q_target - q_predict)
            
        state = next_state
        path.append(state)
        
    path_lengths.append(len(path))
        
    # 每隔10个回合进行一次可视化
    if (episode + 1) % 10 == 0:
        print(f"第{episode + 1}回合：路径长度 = {len(path)}")
        env.render(path, episode + 1)

# 绘制路径长度随回合数的变化
plt.plot(path_lengths)
plt.xlabel('回合数')
plt.ylabel('路径长度')
plt.title('路径长度随训练回合的变化')
plt.show()
