import json
import time

import requests
from bs4 import BeautifulSoup
from shadowsocks import encrypt

from utils import *

def Clawler(input_post_id, input_f_forum_id, ss_config = None):
    if ss_config is not None:
        crypto = encrypt.Encryptor(ss_config["password"], ss_config["method"])

        proxies = {
            "http": f"socks5://{ss_config['server']}:{ss_config['port']}",
            "https": f"socks5://{ss_config['server']}:{ss_config['port']}"
        }

    url = 'https://bbs-api.miyoushe.com/post/wapi/getPostFull'

    params = {
        'gids': '2',
        'post_id': input_post_id,
        'read': '1',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Host': 'bbs-api.miyoushe.com',
        'Origin': 'https://www.miyoushe.com',
        'Referer': 'https://www.miyoushe.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    }

    response = requests.get(url, params=params, headers=headers)
    html = response.text
    data = json.loads(html)

    time.sleep(2)

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
        print('success!')
    return target
