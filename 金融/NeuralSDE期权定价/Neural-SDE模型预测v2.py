import torch
import torch.nn as nn

# 定义 neural SDE 模型
class NeuralSDE(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers):
        super(NeuralSDE, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.drift_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            *[nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU()) 
              for _ in range(num_layers - 1)],
            nn.Linear(hidden_dim, 1)
        )
        
        self.diffusion_net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            *[nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.ReLU())
              for _ in range(num_layers - 1)],
            nn.Linear(hidden_dim, 1),
            nn.Softplus()
        )
        
    def forward(self, x):
        drift = self.drift_net(x)
        diffusion = self.diffusion_net(x)
        return drift, diffusion

# 使用模型进行预测
def predict_price(model, option_params):
    option_params = torch.tensor(option_params, dtype=torch.float32)
    with torch.no_grad():
        drift, diffusion = model(option_params)
    return drift.item()

# 加载模型
input_dim = 4
hidden_dim = 128
num_layers = 3

loaded_model = NeuralSDE(input_dim, hidden_dim, num_layers)
loaded_model.load_state_dict(torch.load("trained_neural_sde.pth"))

# 使用模型进行预测
option_params = [2.02, 132.8, 50, 0.50742]  # 硬编码的预测期权参数
predicted_price = predict_price(loaded_model, option_params)
print(f"Predicted option price: {predicted_price:.4f}")