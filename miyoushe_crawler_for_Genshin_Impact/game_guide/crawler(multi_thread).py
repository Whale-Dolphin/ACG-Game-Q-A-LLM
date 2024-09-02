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

# 全局计数器
total_posts_count = 0
valid_posts_count = 0
count_lock = threading.Lock()

# 每批处理的帖子数量
BATCH_SIZE = 100


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
        self.text = BeautifulSoup(data['data']['post']['post']['content'], 'html.parser').get_text(separator=' ',strip=True)
        self.length = len(self.text)


def generate_fake_ua():
    ua = UserAgent()
    return ua.random


def write_to_file(filename, content, folder='data'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)

    # 将 content 转换为字典格式
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
    return [post_id.strip() for post_id in post_ids]  # 不限制数量


def is_article_valid(article):
    return article.f_forum_id==43 and article.like_num>=50 and len(article.text) >= 100


def fetch_proxies_from_api():
    global proxy_pool
    while True:
        try:
            # API请求
            api_url = ''
            response = requests.get(api_url)
            if response.status_code == 200:
                proxy_data = response.json()
                if proxy_data['code'] == '10001':  # 检查是否成功获取代理
                    proxies = [
                        f"{item['ip']}:{item['port']}" for item in proxy_data['data']['proxy_list']
                    ]
                    with proxy_condition:
                        proxy_pool.extend(proxies)  # 更新代理池
                        proxy_condition.notify_all()  # 通知所有等待的线程
                    print(f"[ProxyUpdater] Updated proxies: {proxy_pool}")
                else:
                    print(f"[ProxyUpdater] Failed to fetch proxies: {proxy_data['msg']}")
            else:
                print(f"[ProxyUpdater] Failed to fetch proxies: {response.status_code}")
        except Exception as e:
            print(f"[ProxyUpdater] Error fetching proxies: {e}")

        time.sleep(11)  # 每11秒请求一次


def get_proxy():
    with proxy_condition:
        while not proxy_pool:
            print("[ProxyGetter] Proxy pool is empty, waiting for new proxies...")
            proxy_condition.wait()  # 等待新的代理IP
        proxy = proxy_pool.pop(0)  # 返回并移除列表中的第一个IP
        print(f"[ProxyGetter] Got proxy: {proxy}")
        return proxy


def crawler(post_id_queue, thread_name):
    global total_posts_count, valid_posts_count

    try:
        proxy = get_proxy()  # 每个线程在开始时获取一个代理IP
        username = ''
        password = ''

        while not post_id_queue.empty():
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
            retry_count = 0  # 添加重试计数
            max_retries = 3  # 设置最大重试次数

            while not success and retry_count < max_retries:
                try:
                    response = requests.get(url, headers=headers, params=params, proxies=proxies)
                    if response.status_code != 200:
                        raise requests.RequestException(f"Failed to fetch data: {response.status_code}")

                    response_json = response.json()
                    if response_json['data'] is None:
                        raise requests.RequestException("Empty response data")

                    game_guide = Game_Guide(response_json)
                    if is_article_valid(game_guide):
                        write_to_file(f'mohiyo-&原神-{post_id}.json', game_guide, 'data')
                        print(f"[{thread_name}] Successfully processed and saved post_id: {post_id}")
                        success = True
                        with count_lock:
                            valid_posts_count += 1
                    else:
                        print(f"[{thread_name}] Invalid article content for post_id: {post_id}")
                        success = True  # 即使内容无效，也标记为成功以避免无限循环

                except requests.RequestException as e:
                    print(f"[{thread_name}] Request failed: {e}, retrying... ({retry_count + 1}/{max_retries})")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"[{thread_name}] Max retries reached, getting a new proxy...")
                        proxy = get_proxy()  # 从代理池获取新IP
                        proxies = {
                            'http': f'http://{username}:{password}@{proxy}',
                            'https': f'http://{username}:{password}@{proxy}'
                        }

            post_id_queue.task_done()
            print(f"[{thread_name}] Finished processing post_id: {post_id}")

            # 随机暂停 1 到 2 秒
            sleep_time = random.uniform(1, 2)
            print(f"[{thread_name}] Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
    except Exception as e:
        print(f"[{thread_name}] Unexpected error: {e}")


def main():
    global total_posts_count, valid_posts_count

    post_ids = get_post_ids()
    total_posts_count = len(post_ids)

    # 启动代理更新线程
    proxy_thread = threading.Thread(target=fetch_proxies_from_api, daemon=True)
    proxy_thread.start()

    processed_count = 0
    while processed_count < total_posts_count:
        post_id_queue = queue.Queue()
        batch_post_ids = post_ids[processed_count:processed_count + BATCH_SIZE]
        for post_id in batch_post_ids:
            post_id_queue.put(post_id)

        threads = []
        max_threads = 5

        for i in range(max_threads):
            thread_name = f"Thread-{i + 1}"
            thread = threading.Thread(target=crawler, args=(post_id_queue, thread_name))
            threads.append(thread)
            thread.start()
            print(f"[{thread_name}] Started")

        post_id_queue.join()  # 等待队列中的所有任务完成

        for thread in threads:
            thread.join()
            print(f"[{thread_name}] Completed")

        print(f"Processed {processed_count + len(batch_post_ids)} posts. Valid posts: {valid_posts_count}")

        # 更新已处理的数量
        processed_count += len(batch_post_ids)

        if processed_count < total_posts_count:
            print("Pausing for 60 seconds...")
            time.sleep(60)  # 暂停60秒

    print("All posts processed.")
    print(f"Total posts processed: {total_posts_count}, Valid posts: {valid_posts_count}")


if __name__ == "__main__":
    main()
