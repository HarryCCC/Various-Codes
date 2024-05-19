import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

'''
def download_file(url):
    response = requests.get(url)
    filename = url.split('=')[-1]  # 假设下载链接格式固定，简单提取id作为文件名
    with open(filename, 'wb') as file:
        file.write(response.content)
        print(f"Downloaded {filename}")
'''

def download_file(url):
    response = requests.get(url)
    # 假设下载的链接指向的是PDF文件，直接在文件名后添加.pdf
    filename = url.split('=')[-1] + ".pdf"
    with open(filename, 'wb') as file:
        file.write(response.content)
        print(f"Downloaded {filename}")

def get_download_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    download_link = soup.find('a', href=lambda href: href and "download" in href)
    if download_link:
        return urljoin(url, download_link['href'])
    return None

def scrape_range(start, end):
    base_url = "https://www.neri.org.cn/"
    for num in range(start, end+1):
        full_url = f"{base_url}{num:0>5}.html"
        print(f"Scraping {full_url}")
        download_url = get_download_links(full_url)
        if download_url:
            download_file(download_url)
        else:
            print("No download link found.")

if __name__ == "__main__":
    # scrape_range(2411, 2525) # 2010/01 - 2019-07
    scrape_range(3289, 3382) # 2019/08 - 2024/04