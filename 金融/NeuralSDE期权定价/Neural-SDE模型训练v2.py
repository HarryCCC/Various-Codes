import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

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

# train model
def train_model(model, dataloader, num_epochs, learning_rate, patience):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    best_loss = float('inf')
    epochs_without_improvement = 0
    
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        for batch in dataloader:
            optimizer.zero_grad()
            x_batch = batch[:, :-1].float()
            y_batch = batch[:, -1].float()
            drift, diffusion = model(x_batch)
            loss = criterion(drift, y_batch.unsqueeze(1))
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        epoch_loss /= len(dataloader)
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}")
        
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            epochs_without_improvement = 0
            torch.save(model.state_dict(), "best_model.pth")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
    
    model.load_state_dict(torch.load("best_model.pth"))
    return model

# 准备数据
file_path = "CallOptionData_apple_2021-2023_with_BSM.csv"
df = pd.read_csv(file_path)
features = ["YearToMaturity", "StockPrice", "StrikePrice", "ImpliedVolatility"]
target = "CallOptionPrice"
dataset = df[features + [target]].values.astype(np.float32)
dataset = torch.tensor(dataset, dtype=torch.float32)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True)

# 训练模型
input_dim = len(features)
hidden_dim = 128
num_layers = 3
num_epochs = 100
learning_rate = 0.001
patience = 10

model = NeuralSDE(input_dim, hidden_dim, num_layers)
trained_model = train_model(model, dataloader, num_epochs, learning_rate, patience)

# 保存模型
torch.save(trained_model.state_dict(), "trained_neural_sde.pth")