import requests
import csv

# 1. 设置 subreddit 名称和请求次数限制
subreddit_name = "python"
max_requests = 100  # 设置最大请求次数为 100

# 2. 初始化请求计数器
request_count = 0

# 3. Reddit API 的基础 URL 和请求头
base_url = f"https://www.reddit.com/r/{subreddit_name}/new/.json"
headers = {'User-Agent': 'Mozilla/5.0'}

# 4. 准备 CSV 文件
csv_file_path = "reddit数据.csv"

# 5. 打开 CSV 文件并准备写入
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['title', 'author', 'score', 'comments', 'permalink']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()  # 写入表头

    # 6. 开始请求循环
    while request_count < max_requests:
        
        # 6.1 发起 GET 请求
        response = requests.get(base_url, headers=headers)
        
        # 6.2 检查请求是否成功
        if response.status_code == 200:
            
            # 解析 JSON 数据并写入 CSV
            posts = response.json()['data']['children']
            for post in posts:
                post_data = post['data']
                writer.writerow({
                    'title': post_data['title'],
                    'author': post_data['author'],
                    'score': post_data['score'],
                    'comments': post_data['num_comments'],
                    'permalink': f"https://reddit.com{post_data['permalink']}"
                })
            
            print(f"Completed request {request_count + 1}")

        else:
            print(f"Failed to fetch data for request {request_count + 1}")
        
        # 6.3 更新请求计数器
        request_count += 1

    print(f"All done! Reddit posts have been saved to {csv_file_path}")
