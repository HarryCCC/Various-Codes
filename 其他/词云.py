from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Convert Chinese keywords to English for demonstration purposes
english_keywords = [
    "Artificial Intelligence", "Large Model", "ChatGPT", "Development Direction", "Human Preference Alignment",
    "Multimodal Large Model", "Safety and Control", "Computational Efficiency", "Deep Learning Framework",
    "Data Fusion", "GPU Chip", "Computational Resources", "Industrial Application", "Natural Language Processing",
    "Model Evaluation", "Digital Transformation", "Market Size", "Technology Gap", "Innovation Capability",
    "Ecosystem Construction"
]

# List of Chinese keywords
keywords = [
    "人工智能", "大模型", "ChatGPT", "发展方向", "人类偏好对齐", "多模态大模型", "安全可控",
    "算力效率", "深度学习框架", "数据融合", "GPU芯片", "算力资源", "产业应用", "自然语言处理",
    "模型评估", "数字化转型", "市场规模", "技术差距", "创新能力", "生态构建"
]
# Create a word cloud
# 这里需要指定中文字体路径，例如 'SimHei' 或 'Microsoft YaHei'
# 如果不确定字体路径，可以将其替换为字体文件的具体路径，例如 '/path/to/SimHei.ttf'
wordcloud = WordCloud(font_path='C:\\Windows\\Fonts\\SimHei.ttf', width = 800, height = 800, 
                background_color ='white', 
                min_font_size = 10).generate(' '.join(keywords))
# Plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()
