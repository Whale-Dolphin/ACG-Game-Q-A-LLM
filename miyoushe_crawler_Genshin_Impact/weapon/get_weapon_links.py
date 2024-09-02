import json

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def write_to_json(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


def get_weapon_links(url='https://bbs.mihoyo.com/ys/obc/channel/map/189/5?bbs_presentation_style=no_header'):
    headers = {
        'User-Agent': UserAgent().random
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        raw_links = soup.select('div.collection-avatar a')
        weapon_links = {}
        for link in raw_links:
            weapon_links[link.select_one('.collection-avatar__title').text.strip()] = f"https://bbs.mihoyo.com{link.get('href')}"
        return weapon_links

    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Other requests error occurred: {e}")
    return None


try:
    weapon_links = get_weapon_links()
    write_to_json('weapon_links.json', weapon_links)
    print(f"weapon page links fetched successfully, {len(weapon_links)} links fetched.")
except Exception as e:
    print(f"Error occurred: {e}")
