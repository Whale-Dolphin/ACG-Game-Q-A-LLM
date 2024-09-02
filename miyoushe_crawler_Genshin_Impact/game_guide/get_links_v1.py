import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# 全局浏览器实例
driver = None

def init_browser():
    global driver
    if driver is None:
        # 初始化Chrome浏览器
        service = Service("")  # 替换为你的chromedriver路径
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 如果不需要浏览器界面，可以启用无头模式
        driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_all_posts(url):
    driver = init_browser()

    # 访问目标页面
    driver.get(url)
    time.sleep(3)  # 等待页面加载
    print("Page loaded successfully")

    # 模拟下滑操作
    for _ in range(10):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)  # 等待新内容加载
        print(f"Scrolling for {_+1} times...")

    # 获取页面内容
    html = driver.page_source

    return html

def parse_html(html, min_likes=400):
    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有帖子
    posts = soup.find_all('div', class_='mhy-article-card')

    print(f"本次获得{len(posts)}条帖子")

    valid_links = []
    for post in posts:
        # 获取点赞数
        try:
            likes = int(post.find('div', class_='mhy-article-card__data-item').find('span').get_text())
        except (AttributeError, ValueError):
            likes = 0

        # 检查点赞数是否大于指定值
        if likes >= min_likes:
            # 提取链接中的数字ID
            link_tag = post.find('a', class_='mhy-router-link mhy-article-card__link')
            link = link_tag['href']
            post_id = re.search(r'/ys/article/(\d+)', link)
            valid_links.append(post_id.group(1))

    return valid_links

def get_links():
    url = 'https://www.miyoushe.com/ys/home/43'
    html = fetch_all_posts(url)
    if html:
        links = parse_html(html)
        return links

def write_links_to_file(links, file_path=''):
    with open(file_path, 'a', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

# for i in range(1000):
#     links = get_links()
#     nums = len(links)
#     print(f'已获得{nums}条帖子链接')
#     write_links_to_file(links)
#     print(f'已写入{nums}条帖子链接')

