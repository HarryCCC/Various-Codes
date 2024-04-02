import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import DataLoader

def heston_model(S0, r, kappa, theta, sigma, rho, T, dt, N):
    # 生成Heston模型的路径
    S = np.zeros((N, T+1))
    V = np.zeros((N, T+1))
    S[:, 0] = S0
    V[:, 0] = theta
    
    for i in range(1, T+1):
        Z1 = np.random.standard_normal(N)
        Z2 = rho * Z1 + np.sqrt(1 - rho**2) * np.random.standard_normal(N)
        V[:, i] = np.maximum(V[:, i-1] + kappa * (theta - V[:, i-1]) * dt + sigma * np.sqrt(V[:, i-1] * dt) * Z1, 0)
        S[:, i] = S[:, i-1] * np.exp((r - 0.5 * V[:, i-1]) * dt + np.sqrt(V[:, i-1] * dt) * Z2)
    
    return S, V

def generate_data(S0, r, kappa, theta, sigma, rho, T, dt, N, M):
    # 生成训练数据
    S, V = heston_model(S0, r, kappa, theta, sigma, rho, T, dt, N)
    
    # 计算香草期权价格
    K = np.linspace(0.8*S0, 1.2*S0, M)  # 生成行权价
    C = np.zeros((M, T+1))
    
    for i in range(M):
        for j in range(T+1):
            C[i, j] = np.mean(np.maximum(S[:, j] - K[i], 0))
    
    return C

# Heston模型参数
S0 = 1.0  # 初始资产价格
r = 0.025  # 无风险利率 
kappa = 0.3  # 均值回归速度
theta = 0.04  # 长期均值
sigma = 0.1  # 波动率的波动率
rho = -0.5  # 两个布朗运动的相关系数

T = 100  # 时间步数
dt = 0.01  # 时间步长  
N = 10000  # 模拟路径数
M = 21  # 行权价数量

market_prices = generate_data(S0, r, kappa, theta, sigma, rho, T, dt, N, M)

class SDE_Model(nn.Module):
    def __init__(self, dim, num_layers, activation):
        super(SDE_Model, self).__init__()
        self.dim = dim
        self.num_layers = num_layers
        self.activation = activation
        
        self.drift_net = self._make_net()
        self.diffusion_net = self._make_net()
        
    def _make_net(self):
        layers = []
        for i in range(self.num_layers):
            layers.append(nn.Linear(self.dim, self.dim))
            layers.append(self.activation)
        return nn.Sequential(*layers)
    
    def drift(self, t, x):
        return self.drift_net(x)
    
    def diffusion(self, t, x):
        return self.diffusion_net(x)
    
def euler_maruyama(model, x0, dt, num_steps, num_paths):
    x = x0.repeat(num_paths, 1)
    dW = np.sqrt(dt) * torch.randn(num_steps, num_paths, model.dim)
    for i in range(num_steps):
        t = i * dt
        drift = model.drift(t, x)
        diffusion = model.diffusion(t, x)
        x = x + drift * dt + diffusion * dW[i]
    return x

def train(model, market_prices, x0, dt, num_steps, num_paths, epochs, lr, patience):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=patience, verbose=True)
    
    best_loss = float('inf')
    for epoch in range(epochs):
        x = euler_maruyama(model, x0, dt, num_steps, num_paths)
        
        # 计算损失
        loss = 0
        for i in range(market_prices.shape[0]):
            payoff = torch.mean(torch.max(x - torch.tensor(market_prices[i, -1]), torch.zeros_like(x)))
            loss += (payoff - torch.tensor(market_prices[i, -1])).pow(2)
        loss /= market_prices.shape[0]
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss {loss.item():.4f}")
        
        # 更新学习率调度器
        scheduler.step(loss)
        
        # 保存最佳模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), 'neural_sde_model.pth')
        
        # 若学习率降到最低值依旧没有改善，则停止训练
        if optimizer.param_groups[0]['lr'] < 1e-6:
            print("Early stopping")
            break
            
dim = 1  
num_layers = 4
activation = nn.ReLU()
model = SDE_Model(dim, num_layers, activation)

x0 = torch.ones(1)
dt = 0.01
num_steps = 100
num_paths = 1000
epochs = 10000
lr = 0.001
patience = 100  # 学习率降低等待次数

train(model, market_prices, x0, dt, num_steps, num_paths, epochs, lr, patience)