import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize

# 下载 NLTK 的 punkt 数据包，用于分词
nltk.download('punkt')

# 函数：清洗文本
def clean_text(text):
    text = re.sub(r'http\S+', '', text)  # 去除 URLs
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    text = re.sub(r'\d+', '', text)      # 去除数字
    return text

# 函数：分词
def tokenize(text):
    return word_tokenize(text)

# 函数：标准化（转小写）
def normalize(text):
    return text.lower()

# 函数：完整的文本预处理流程
def preprocess_text(text):
    text = clean_text(text)
    text = normalize(text)
    tokens = tokenize(text)
    return ' '.join(tokens)

def main():
    # Replace these lines with actual data loading
    reddit_df = pd.read_csv("reddit数据.csv")
    news_df = pd.read_csv("新闻数据.csv")

    # Apply text preprocessing to the 'title' and 'description' columns
    reddit_df['processed_title'] = reddit_df['title'].apply(preprocess_text)
    news_df['processed_title'] = news_df['title'].apply(preprocess_text)
    news_df['processed_description'] = news_df['description'].apply(preprocess_text)

    # Save processed DataFrames to CSV files
    reddit_df.to_csv("reddit数据_已处理.csv", index=False)
    news_df.to_csv("新闻数据_已处理.csv", index=False)

if __name__ == "__main__":
    main()
