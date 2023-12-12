# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# 定义一个正态分布的似然函数
def likelihood(mu, sigma, x):
  return norm.pdf(x, mu, sigma)

# 定义一个正态分布的先验分布
def prior(mu, sigma0, mu0):
  return norm.pdf(mu, mu0, sigma0)

# 定义一个正态分布的后验分布
def posterior(mu, sigma, sigma0, mu0, x):
  n = len(x) # 样本的个数
  xbar = np.mean(x) # 样本的均值
  mu_n = (sigma0**2 * xbar + sigma**2 * mu0) / (n * sigma0**2 + sigma**2) # 后验分布的均值
  sigma_n = np.sqrt((sigma0**2 * sigma**2) / (n * sigma0**2 + sigma**2)) # 后验分布的标准差
  return norm.pdf(mu, mu_n, sigma_n)

# 定义一个测量温度的实验
sigma = 0.5 # 似然函数的标准差，假设已知
sigma0 = 1 # 先验分布的标准差，假设已知
mu0 = 20 # 先验分布的均值，假设已知
x = np.array([19.8, 20.4, 19.6, 19.9, 20.3]) # 观测到的温度数据

# 计算不同的mu值下的似然函数、先验分布和后验分布
mus = np.linspace(15, 25, 200) # mu的取值范围
likes = [np.prod([likelihood(mu, sigma, xi) for xi in x]) for mu in mus] # 似然函数的值，使用乘积来表示联合概率
priors = [prior(mu, sigma0, mu0) for mu in mus] # 先验分布的值
posts = [posterior(mu, sigma, sigma0, mu0, x) for mu in mus] # 后验分布的值

# 绘制不同的mu值下的似然函数、先验分布和后验分布
plt.figure(figsize=(10, 10)) # 设置图像的大小
plt.plot(mus, likes, label="Likelihood", color="blue") # 绘制似然函数
plt.plot(mus, priors, label="Prior", color="red") # 绘制先验分布
plt.plot(mus, posts, label="Posterior", color="green") # 绘制后验分布
plt.xlabel("Mu") # 设置x轴的标签
plt.ylabel("Density") # 设置y轴的标签
plt.legend() # 显示图例
plt.show() # 显示图像
