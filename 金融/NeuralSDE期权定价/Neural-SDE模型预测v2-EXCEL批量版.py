import torch
import torch.nn as nn
import pandas as pd

# define neural SDE model
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

# predict with model
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

# 读取完整的CSV文件
file_path = "CallOptionData_apple_2021-2023_with_BSM.csv"
df = pd.read_csv(file_path)

# 提取所需的列
option_data = df[['YearToMaturity', 'StockPrice', 'StrikePrice', 'ImpliedVolatility']].values

# 对每行数据进行预测
predictions = []
for params in option_data:
    predicted_price = predict_price(loaded_model, params)
    predictions.append(predicted_price)

# 将预测结果添加到DataFrame的新列中
df['NeuralSDE_Pricing'] = predictions

# 保存更新后的DataFrame到新的CSV文件
output_file_path = "CallOptionData_apple_2021-2023_with_BSM&NSDE.csv"
df.to_csv(output_file_path, index=False)

print("预测完成,结果已保存到文件:", output_file_path)