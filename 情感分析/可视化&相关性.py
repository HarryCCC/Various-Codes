import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体为 SimHei
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

# Function to convert "Sentiment_Label" to integer
def convert_label_to_int(label):
    return int(label.split(" ")[0])

# Function to analyze the correlation between sentiment label and score
def analyze_correlation(df):
    df['Sentiment_Label_Int'] = df['Sentiment_Label'].apply(convert_label_to_int)
    correlation = df['Sentiment_Label_Int'].corr(df['Sentiment_Score'])
    return correlation

# Function to convert star ratings to natural language descriptions
def convert_star_to_description(star):
    mapping = {
        "1 star": "Very Negative",
        "2 stars": "Negative",
        "3 stars": "Neutral",
        "4 stars": "Positive",
        "5 stars": "Very Positive"
    }
    return mapping.get(star, "Unknown")

# Function to categorize sentiment strength into four quartiles
def categorize_strength(strength):
    if 0 <= strength < 0.25:
        return "Very Low"
    elif 0.25 <= strength < 0.5:
        return "Low"
    elif 0.5 <= strength < 0.75:
        return "Moderate"
    else:
        return "High"

# Function to visualize sentiment and strength distribution in pie charts
def visualize_sentiment_and_strength(df, title_prefix):
    correlation = analyze_correlation(df)
    correlation_text = f"情感类别与情感强度的相关性为：{correlation:.3f}"
    #对于reddit和news，情感类别与情感强度的相关性分别为：0.562和0.133
    #一些结论：：：
    #Reddit在表达正面（强烈）情感（由于缺乏reddit上负面观点的数据）时，其词汇运用和语气可能更加松弛开放；
    #而新闻表达，可能在情感抒发时（不同情绪下，即使是极端情绪下），对词汇的斟酌则更为抑制。
    #新闻的极端情绪（非常积极/消极）总占比约四分之三，因为更有需要抓取观众吸引力的需求。
    
    # Convert star ratings to natural language descriptions

    df['Sentiment_Description'] = df['Sentiment_Label'].apply(convert_star_to_description)
    
    # Categorize sentiment strength
    df['Sentiment_Strength_Category'] = df['Sentiment_Score'].apply(categorize_strength)
    
    # Create subplots for overall sentiment distribution and sentiment strength distribution
    fig, axs = plt.subplots(2, 3, figsize=(12, 8))
    plt.subplots_adjust(hspace=0.5)  # Adjust vertical space between subplots
    
    # Display correlation as a text at the center
    plt.figtext(0.5, 0.5, correlation_text, ha="center", va="center", fontsize=12)

    
    # Pie chart for overall sentiment distribution
    sentiment_counts = df['Sentiment_Description'].value_counts()
    axs[0, 0].pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%')
    axs[0, 0].set_title(f"{title_prefix}\n Overall \n Sentiment Distribution")
    
    # Pie charts for sentiment strength distribution within each sentiment
    sentiments = sentiment_counts.index
    for i, sentiment in enumerate(sentiments, 1):
        strength_counts = df[df['Sentiment_Description'] == sentiment]['Sentiment_Strength_Category'].value_counts()
        axs[i // 3, i % 3].pie(strength_counts, labels=strength_counts.index, autopct='%1.1f%%')
        axs[i // 3, i % 3].set_title(f"{title_prefix} \n{sentiment} \nSentiment Strength Distribution")

    plt.show()

# Read processed data
reddit_df = pd.read_csv("reddit数据_多类别多强度情感分析.csv")
news_df = pd.read_csv("新闻数据_多类别多强度情感分析.csv")

# Visualize sentiment and strength for Reddit and News data
visualize_sentiment_and_strength(reddit_df, "Reddit")
visualize_sentiment_and_strength(news_df, "News")
