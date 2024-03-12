from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 你的QQ号和密码
qq_number = 'xxx'  
qq_password = 'yyy'

# 登录QQ空间
browser = webdriver.Chrome()
browser.get('http://i.qq.com')
browser.switch_to.frame('login_frame')
browser.find_element(By.ID, 'switcher_plogin').click()
browser.find_element(By.ID, 'u').send_keys(qq_number)
browser.find_element(By.ID, 'p').send_keys(qq_password)
browser.find_element(By.ID, 'login_button').click()
time.sleep(5)

# 打开说说页面
browser.get('https://user.qzone.qq.com/' + qq_number + '/311')
time.sleep(2)
browser.switch_to.frame('app_canvas_frame')

# 爬取内容并保存到文本文件
with open('shuoshuo_text.txt', 'w', encoding='utf-8') as f:
    for page in range(16):  # 爬取前n页
        if page > 0:
            # 点击下一页
            next_page_btn = browser.find_element(By.LINK_TEXT, '下一页')
            next_page_btn.click()
            time.sleep(2)

        # 获取页面文本并写入文件
        page_text = browser.find_element(By.XPATH, '//body').text
        f.write(f'第{page+1}页内容:\n')
        f.write(page_text)
        f.write('\n\n')

print('说说文本已保存到shuoshuo_text.txt')

browser.quit()