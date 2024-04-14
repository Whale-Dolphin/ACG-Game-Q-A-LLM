import json
import time
import logging

import requests
from bs4 import BeautifulSoup
from shadowsocks import encrypt

from utils import *

log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_filename = "miyoushe_crawler.log"

logging.basicConfig(level=logging.INFO, format=log_format, filename=log_filename, filemode='a')

logger = logging.getLogger()

def Clawler(input_post_id, input_f_forum_id, ss_config = None, proxy_info = None):
    if ss_config is not None:
        crypto = encrypt.Encryptor(ss_config["password"], ss_config["method"])

        proxies = {
            "http": f"socks5://{ss_config['server']}:{ss_config['port']}",
            "https": f"socks5://{ss_config['server']}:{ss_config['port']}"
        }

    if proxy_info is not None:
        proxies = {
            'http': f'http://{proxy_info["server"]}:{proxy_info["port"]}',
            'https': f'http://{proxy_info["server"]}:{proxy_info["port"]}'
        }

    tunnel = "a757.kdltps.com:15818"

    username = "t11298763855356"
    password = "x42bynmf"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }


    url = 'https://bbs-api.miyoushe.com/post/wapi/getPostFull'

    params = {
        'gids': '2',
        'post_id': input_post_id,
        'read': '1',
    }

    headers = {
        'Referer': 'https://www.miyoushe.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    }

    response = requests.get(url, params=params, headers=headers, proxies=proxies)
    
    # if proxy_info is not None:
    #     response = requests.get(url, params=params, headers=headers, proxies=proxies)
    # else:
    #     response = requests.get(url, params=params, headers=headers)
    html = response.text
    data = json.loads(html)
    # print(data)

    time.sleep(0.5)

    if data['data'] == None:
        return None

    content_html = data['data']['post']['post']['content']
    html_soup = BeautifulSoup(content_html, 'html.parser')
    text = html_soup.get_text(separator=" ", strip=True)
    game_id = data['data']['post']['post']['game_id']
    post_id = data['data']['post']['post']['post_id']
    f_forum_id = data['data']['post']['post']['f_forum_id']
    subject = data['data']['post']['post']['subject']
    url = 'https://www.miyoushe.com/ys/article/' + str(post_id)
    created_at = data['data']['post']['post']['created_at']
    like_num = data['data']['post']['stat']['like_num']
    length = len(text)

    target = Article(game_id, post_id, f_forum_id, subject,
                 url, text, created_at, like_num, length)

    if target.f_forum_id != input_f_forum_id:
        return None
    elif len(target.text) < 100:
        return None
    elif target.like_num < 50:
        return None
    else:
        logger.info(f"Successfully fetched post {post_id}")
    return target
