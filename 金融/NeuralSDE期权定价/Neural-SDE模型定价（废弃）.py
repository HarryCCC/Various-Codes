import torch
import torch.nn as nn
import numpy as np

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

def price_option(model, x0, dt, num_steps, num_paths, strike):
    model.load_state_dict(torch.load('neural_sde_model.pth'))  # 加载模型
    model.eval()
    x = euler_maruyama(model, x0, dt, num_steps, num_paths)
    payoff = torch.max(x - strike, torch.zeros_like(x))
    return payoff.mean().item()

dim = 1
num_layers = 4
activation = nn.ReLU()
model = SDE_Model(dim, num_layers, activation)

# 硬编码期权参数
x0 = torch.tensor([1.0])  # 期权初始价格
dt = 0.01  # 时间步长
num_steps = 36  # 总步数
num_paths = 100000  # 模拟路径数
strike = 1.013  # 期权行权价

option_price = price_option(model, x0, dt, num_steps, num_paths, strike)
print(f"期权价格: {option_price:.4f}")