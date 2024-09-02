import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import os
import threading
import queue
import random
import json

# 全局代理池和条件变量
proxy_pool = []
proxy_condition = threading.Condition()

# 用于控制线程的全局标志
terminate_threads = threading.Event()

class Game_Guide:
    def __init__(self, data):
        self.game_id = data['data']['post']['post']['game_id']
        self.post_id = data['data']['post']['post']['post_id']
        self.f_forum_id = data['data']['post']['post']['f_forum_id']
        self.subject = data['data']['post']['post']['subject']
        self.url = 'https://www.miyoushe.com/ys/article/' + str(self.post_id)
        self.created_at = data['data']['post']['post']['created_at']
        self.like_num = data['data']['post']['stat']['like_num']
        self.view_num = data['data']['post']['stat']['view_num']
        self.reply_num = data['data']['post']['stat']['reply_num']
        self.text = BeautifulSoup(data['data']['post']['post']['content'], 'html.parser').get_text(separator=' ', strip=True)
        self.length = len(self.text)

def generate_fake_ua():
    ua = UserAgent()
    return ua.random

def write_to_file(filename, content, folder='data'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)

    content_dict = {
        "game_id": content.game_id,
        "post_id": content.post_id,
        "f_forum_id": content.f_forum_id,
        "subject": content.subject,
        "url": content.url,
        "created_at": content.created_at,
        "like_num": content.like_num,
        "view_num": content.view_num,
        "reply_num": content.reply_num,
        "text": content.text,
        "length": content.length
    }

    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(content_dict, file, ensure_ascii=False, indent=4)

def get_post_ids():
    with open('sorted_data(min_view_num=0, min_like_num=50, min_reply_num=0).txt', 'r', encoding='utf-8') as file:
        post_ids = file.readlines()
    return [post_id.strip() for post_id in post_ids]

def is_article_valid(article):
    return len(article.text) >= 100

def fetch_proxies_from_api():
    global proxy_pool
    while not terminate_threads.is_set():
        try:
            api_url = ''
            response = requests.get(api_url)
            response.raise_for_status()  # 检查请求状态
            proxy_data = response.json()
            if proxy_data['code'] == '10001':
                proxies = [f"{item['ip']}:{item['port']}" for item in proxy_data['data']['proxy_list']]
                with proxy_condition:
                    proxy_pool.extend(proxies)
                    proxy_condition.notify_all()
                print(f"[ProxyUpdater] Updated proxies: {proxy_pool}")
            else:
                print(f"[ProxyUpdater] Failed to fetch proxies: {proxy_data['msg']}")
        except requests.RequestException as e:
            print(f"[ProxyUpdater] Error fetching proxies: {e}")

        time.sleep(11)

def get_proxy():
    with proxy_condition:
        while not proxy_pool and not terminate_threads.is_set():
            print("[ProxyGetter] Proxy pool is empty, waiting for new proxies...")
            proxy_condition.wait()
        if proxy_pool:
            proxy = proxy_pool.pop(0)
            print(f"[ProxyGetter] Got proxy: {proxy}")
            return proxy
        return None  # 处理终止信号的情况

def crawler(post_id_queue, thread_name):
    try:
        proxy = get_proxy()
        if proxy is None:
            return
        username = ''
        password = ' '

        while not post_id_queue.empty() and not terminate_threads.is_set():
            post_id = post_id_queue.get()
            print(f"[{thread_name}] Processing post_id: {post_id}")

            proxies = {
                'http': f'http://{username}:{password}@{proxy}',
                'https': f'http://{username}:{password}@{proxy}'
            }

            url = 'https://bbs-api.miyoushe.com/post/wapi/getPostFull'
            params = {
                'gids': '2',
                'post_id': post_id,
                'read': '1',
            }

            headers = {
                'Referer': 'https://www.miyoushe.com/',
                'User-Agent': generate_fake_ua()
            }

            success = False
            retry_count = 0
            max_retries = 3

            while not success and retry_count < max_retries and not terminate_threads.is_set():
                try:
                    with requests.get(url, headers=headers, params=params, proxies=proxies, timeout=10) as response:
                        response.raise_for_status()
                        response_json = response.json()
                        if response_json['data'] is None:
                            raise requests.RequestException("Empty response data")

                        game_guide = Game_Guide(response_json)
                        if is_article_valid(game_guide):
                            write_to_file(f'mohiyo-&原神-{post_id}.json', game_guide, 'data')
                            print(f"[{thread_name}] Successfully processed and saved post_id: {post_id}")
                            success = True
                        else:
                            print(f"[{thread_name}] Invalid article content for post_id: {post_id}")
                            success = True

                except requests.RequestException as e:
                    print(f"[{thread_name}] Request failed: {e}, retrying... ({retry_count + 1}/{max_retries})")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"[{thread_name}] Max retries reached, getting a new proxy...")
                        proxy = get_proxy()
                        if proxy is None:
                            break
                        proxies = {
                            'http': f'http://{username}:{password}@{proxy}',
                            'https': f'http://{username}:{password}@{proxy}'
                        }

            post_id_queue.task_done()
            print(f"[{thread_name}] Finished processing post_id: {post_id}")

            sleep_time = random.uniform(1, 2)
            print(f"[{thread_name}] Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
    except Exception as e:
        print(f"[{thread_name}] Unexpected error: {e}")

def manage_threads(post_id_queue):
    global terminate_threads
    while not post_id_queue.empty():
        threads = []
        max_threads = 5
        terminate_threads.clear()  # 重置线程终止标志

        for i in range(max_threads):
            thread_name = f"Thread-{i + 1}"
            thread = threading.Thread(target=crawler, args=(post_id_queue, thread_name))
            threads.append(thread)
            thread.start()
            print(f"[{thread_name}] Started")

        # 10分钟后结束所有线程
        time.sleep(600)
        terminate_threads.set()  # 通知所有线程终止
        print("--------------------------")
        print("Terminating all threads...")
        print("--------------------------")

        for thread in threads:
            thread.join(timeout=30)  # 等待线程结束，设置超时
            if thread.is_alive():
                print(f"[{thread.name}] did not finish within the timeout period.")
            else:
                print(f"[{thread.name}] Completed")

        # 等待30秒
        print("--------------------------")
        print("Waiting for 30 seconds before starting new threads...")
        print("--------------------------")
        time.sleep(30)

        print("--------------------------")
        print("Starting new threads...")
        print("--------------------------")
        terminate_threads.clear()  # 在启动新线程之前清除标志

def main():
    post_ids = get_post_ids()
    post_id_queue = queue.Queue()

    for post_id in post_ids:
        post_id_queue.put(post_id)

    proxy_thread = threading.Thread(target=fetch_proxies_from_api, daemon=True)
    proxy_thread.start()

    manage_threads(post_id_queue)

    print("All threads completed.")

if __name__ == "__main__":
    main()


