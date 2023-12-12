import requests
from bs4 import BeautifulSoup

def crawl_news_titles(url):
    news_titles = []
    try:
        # 在调用 requests.get 函数之前，打印出目标网站的 URL
        print(f"Crawling URL: {url}")
        # 使用 requests 库获取网页的 HTML 代码
        response = requests.get(url)
        # 使用 Beautiful Soup 库解析网页
        soup = BeautifulSoup(response.text, 'html.parser')
        # 使用 find_all 方法查找所有的新闻标题
        titles = soup.find_all('h3')
        # 遍历所有的新闻标题
        for title in titles:
            # 使用 text 属性获取文本内容
            text = title.text
            # 将新闻标题添加到新闻标题列表中
            news_titles.append(text)
    # 在发生异常时，打印出异常信息
    except Exception as e:
        print(f"Error: {e}")
        return news_titles
    
    # 在解析完网页后，打印出网页的 HTML 代码
    print(soup.prettify())
    # 在返回新闻标题列表之前，打印出新闻标题列表
    print(f"News titles: {news_titles}")
    return news_titles



# 设置目标网站的 URL
# url = "http://news.cnr.cn"
url = "http://www.bing.com"

# 调用爬虫函数，爬取新闻标题
news_titles = crawl_news_titles(url)

# 打印所有新闻标题
for title in news_titles:
    print(title)

