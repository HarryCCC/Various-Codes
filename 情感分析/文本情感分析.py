import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# 检查是否有可用的GPU
device = 0 if torch.cuda.is_available() else -1
if device == 0:
    print("GPU is available. The sentiment analysis model will run on the GPU.")
else:
    print("GPU is not available. The sentiment analysis model will run on the CPU.")

# 指定多类别情感分析模型
multi_class_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"

# 初始化模型和分词器
print("Initializing the model and tokenizer.")
tokenizer = AutoTokenizer.from_pretrained(multi_class_model_name)
model = AutoModelForSequenceClassification.from_pretrained(multi_class_model_name)

# 创建管道
print("Creating the sentiment analysis pipeline.")
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=device)

def apply_sentiment_analysis(text):
    result = classifier(text)
    label = result[0]['label']
    score = result[0]['score']
    return label, score

# 读取数据
print("Reading data files. This part runs on CPU.")
reddit_df = pd.read_csv("reddit数据_已处理.csv")
news_df = pd.read_csv("新闻数据_已处理.csv")

# 对Reddit数据应用多类别情感分析和情感强度分析
print("Applying sentiment analysis on Reddit data.")
reddit_df['Sentiment_Label'], reddit_df['Sentiment_Score'] = zip(*reddit_df['title'].apply(apply_sentiment_analysis))

# 对新闻数据应用多类别情感分析和情感强度分析
print("Applying sentiment analysis on News data.")
news_df['Sentiment_Label'], news_df['Sentiment_Score'] = zip(*news_df['title'].apply(apply_sentiment_analysis))

# 将带有情感分析的数据保存到新的CSV文件
print("Saving the data with sentiment analysis into new CSV files.")
reddit_df.to_csv("reddit数据_多类别多强度情感分析.csv", index=False)
news_df.to_csv("新闻数据_多类别多强度情感分析.csv", index=False)

print("Sentiment analysis completed.")

