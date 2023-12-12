import requests
import csv

# 1. 设置API Key
api_key = "8b916fa0ca2e4aa5927a673a08526545"  # 请用你自己的API key替换这里

# 2. 构建API请求
base_url = "https://newsapi.org/v2/everything?"
parameters = {
    "q": "technology",
    "language": "en",
    "sortBy": "publishedAt",
    "apiKey": api_key
}

# 3. 初始化请求计数器和限制
request_count = 0
max_requests = 100  # 设置最大请求数量为100

# 4. CSV文件路径
csv_file_path = '新闻数据.csv'

# 5. 打开CSV文件并准备写入
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['title', 'description', 'url', 'publishedAt']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()  # 写入表头

    # 6. 开始请求循环
    while request_count < max_requests:
        response = requests.get(base_url, params=parameters)
        request_count += 1  # 更新请求计数器

        # 6.1 解析响应
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data["articles"]

            # 6.2 写入数据到CSV
            for article in articles:
                writer.writerow({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'publishedAt': article['publishedAt']
                })

            print(f"Completed request {request_count}")

        else:
            print(f"Failed to fetch news for request {request_count}")

    print(f"All done! News data has been saved to {csv_file_path}")
