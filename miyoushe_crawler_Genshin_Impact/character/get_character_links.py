import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def write_to_file(file_name, data):
    with open(file_name, 'w') as f:
        for link in data:
            f.write(f"https://bbs.mihoyo.com{link}\n")


def get_character_links(url='https://bbs.mihoyo.com/ys/obc/channel/map/189/25?bbs_presentation_style=no_header'):
    headers = {
        'User-Agent': UserAgent().random
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        raw_links = soup.find('div', class_='collection-avatar').find_all('a')
        character_links = []
        for link in raw_links:
            character_links.append(link.get('href'))
        return character_links

    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Other requests error occurred: {e}")
    return None

try:
    write_to_file('character_links.txt',get_character_links())
    print("Character page links fetched successfully")
except Exception as e:
    print(f"Error occurred: {e}")