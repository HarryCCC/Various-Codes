# 导入所需的库
import numpy as np
import matplotlib.pyplot as plt

# 定义目标函数，假设是一个多峰函数
def objective(x):
    return x * np.sin(10 * np.pi * x) + 2.0

# 定义种群的大小，变量的范围，迭代的次数，变异的概率和交叉的概率
pop_size = 100
x_min, x_max = -1.0, 2.0
max_iter = 100
p_mutation = 0.1
p_crossover = 0.8

# 初始化种群，每个个体是一个随机的浮点数
population = np.random.uniform(x_min, x_max, size=pop_size)

# 迭代演化过程
for i in range(max_iter):
    # 评估种群，计算每个个体的适应度
    fitness = objective(population)
    # 选择父代，使用轮盘赌法，根据适应度的大小，赋予每个个体不同的选择概率
    selection_prob = fitness / np.sum(fitness)
    parents = np.random.choice(population, size=pop_size, p=selection_prob)
    # 变异父代，对每个个体进行一定概率的随机扰动
    mutation = parents + np.random.normal(0, 0.1, size=pop_size) * p_mutation
    # 交叉父代，对每对相邻的个体进行一定概率的均匀交叉
    crossover = np.copy(parents)
    for j in range(0, pop_size, 2):
        if np.random.rand() < p_crossover:
            alpha = np.random.rand()
            crossover[j] = alpha * parents[j] + (1 - alpha) * parents[j+1]
            crossover[j+1] = alpha * parents[j+1] + (1 - alpha) * parents[j]
    # 替换种群，使用精英策略，保留当前最优的个体，其余的用变异子和交叉子替换
    offspring = np.concatenate([mutation, crossover])
    best_index = np.argmax(fitness)
    best_individual = population[best_index]
    population = np.delete(offspring, best_index)
    population = np.append(population, best_individual)
    # 打印当前的迭代次数和最优的个体
    print("Iteration:", i+1, "Best individual:", best_individual)

# 绘制目标函数和最终的种群分布
x = np.linspace(x_min, x_max, 1000)
y = objective(x)
plt.plot(x, y, label="Objective")
plt.scatter(population, objective(population), color="red", label="Population")
plt.legend()
plt.show()
