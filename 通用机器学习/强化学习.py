# 导入所需的库
import numpy as np
import gym

# 创建一个环境，假设是一个走迷宫的游戏
env = gym.make("FrozenLake-v1")

# 定义智能体的策略，假设是一个随机的策略，即在每个状态下，以相同的概率选择任意一个动作
policy = np.ones((env.observation_space.n, env.action_space.n)) / env.action_space.n

# 定义智能体的价值函数，假设是一个全零的函数，即在每个状态下，预期的累积奖励都是零
value = np.zeros(env.observation_space.n)

# 定义一个折扣因子，用于衡量未来奖励的重要性
gamma = 0.9

# 定义一个迭代次数，用于控制价值迭代的终止条件
max_iter = 100

# 迭代更新价值函数
for i in range(max_iter):
    # 创建一个新的价值函数，用于存储更新后的值
    new_value = np.zeros(env.observation_space.n)
    # 对每个状态进行更新
    for s in range(env.observation_space.n):
        # 计算每个动作的期望价值，即在当前状态下，执行该动作后，预期的累积奖励
        action_values = np.zeros(env.action_space.n)
        for a in range(env.action_space.n):
            # 获取该动作的转移概率，下一个状态，即时奖励和是否终止的信息
            transitions = env.P[s][a]
            for prob, next_s, reward, done in transitions:
                # 累加该动作的期望价值
                action_values[a] += prob * (reward + gamma * value[next_s])
        # 根据策略的概率，计算当前状态的期望价值，即在当前状态下，按照策略选择任意一个动作后，预期的累积奖励
        state_value = np.sum(policy[s] * action_values)
        # 将当前状态的期望价值存储到新的价值函数中
        new_value[s] = state_value
    # 计算价值函数的变化量，用于判断是否收敛
    delta = np.max(np.abs(new_value - value))
    # 将新的价值函数赋值给旧的价值函数
    value = new_value
    # 打印当前的迭代次数和价值函数的变化量
    print("Iteration:", i+1, "Delta:", delta)

# 输出最终的价值函数
print("Final value function:")
print(value)
