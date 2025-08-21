import numpy as np
import matplotlib.pyplot as plt

# 设置每个模型在不同维度上的得分
dimensions = ['Fitting Market Prices', 'Robustness', 'Interpretability', 'Computational Efficiency', 'Parameter Selection', 'Hedging Performance']
traditional_scores = [0, 0, 1, 1, 1, 0] 
neural_scores = [1, 1, -1, 0, -1, 1]

# 将极坐标根据维度数等分
angles = np.linspace(0, 2*np.pi, len(dimensions), endpoint=False)
angles = np.append(angles,angles[0])

# 在末尾添加第一个值使图形中线条闭合
traditional_scores.append(traditional_scores[0])
neural_scores.append(neural_scores[0])

# 绘图
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(polar=True)
ax.plot(angles, traditional_scores, 'o-', linewidth=2, label='Traditional SDE')
ax.fill(angles, traditional_scores, alpha=0.25)
ax.plot(angles, neural_scores, 'o-', linewidth=2, label='Neural SDE')
ax.fill(angles, neural_scores, alpha=0.25)

# 设置雷达图样式
ax.set_thetagrids(angles * 180/np.pi, dimensions + [''])
ax.set_ylim(-1.5,1.5)
ax.grid(True)
plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

# 显示图形
plt.show()