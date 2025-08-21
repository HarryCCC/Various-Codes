import matplotlib.pyplot as plt
import numpy as np

# 数据
models = ['BSM', 'Neural SDE']
mae_values = [4.8145847856290205, 2.3591109546310847]
mse_values = [50.81694336932885, 15.904566623434674]
mape_values = [24.186009565873157, 7.260611924049842]
r2_values = [0.946204234451934, 0.9831631286636123]

# 绘图
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

x = np.arange(len(models))
width = 0.35

axes[0, 0].bar(x - width/2, mae_values, width, label='MAE')
axes[0, 0].set_ylabel('MAE')
axes[0, 0].set_title('Mean Absolute Error (MAE)')
axes[0, 0].set_xticks(x)
axes[0, 0].set_xticklabels(models)
axes[0, 0].legend()

axes[0, 1].bar(x - width/2, mse_values, width, label='MSE')
axes[0, 1].set_ylabel('MSE')
axes[0, 1].set_title('Mean Squared Error (MSE)')
axes[0, 1].set_xticks(x)
axes[0, 1].set_xticklabels(models)
axes[0, 1].legend()

axes[1, 0].bar(x - width/2, mape_values, width, label='MAPE')
axes[1, 0].set_ylabel('MAPE')
axes[1, 0].set_title('Mean Absolute Percentage Error (MAPE)')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(models)
axes[1, 0].legend()

axes[1, 1].bar(x - width/2, r2_values, width, label='R-squared')
axes[1, 1].set_ylabel('R-squared')
axes[1, 1].set_title('R-squared')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(models)
axes[1, 1].legend()

fig.tight_layout()
plt.show()