import json
import time

import psutil
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver


def fetch_page(url, proxy=None, headers=None, headless=True):
    """
    使用 Selenium 获取网页内容，并可以设置代理和请求头。

    参数：
    url (str): 需要抓取的网页 URL。
    proxy (str, optional): 代理服务器地址，例如 'http://username:password@proxy_ip:proxy_port'。
    headers (dict, optional): 请求头字典，例如 {'User-Agent': 'your-custom-user-agent'}。
    headless (bool, optional): 是否使用无头模式，默认为 True。

    返回：
    str: 网页的 HTML 内容。若发生异常，返回 None。
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    chrome_driver_path = ""  # 替换为你的 chromedriver 路径
    service = Service(chrome_driver_path)

    if not headers:
        headers = {'User-Agent': UserAgent().random}

    driver: WebDriver = None
    page_content = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(2560, 1440)  # 设置窗口大小

        if headers:
            # 使用 Chrome DevTools Protocol 设置请求头
            driver.execute_cdp_cmd('Network.enable', {})
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers})

        driver.get(url)

        # # 等待页面加载完成，直到关键元素存在
        # WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))  # 可以根据实际需要更改选择器
        # )

        # 等待 5 秒，确保页面加载完成
        time.sleep(5)
        page_content = driver.page_source

    except NoSuchElementException as e:
        print(f"[Error] No such element: {e}")
    except TimeoutException as e:
        print(f"[Error] Timeout occurred: {e}")
    except WebDriverException as e:
        print(f"[Error] WebDriver exception: {e}")
    except Exception as e:
        print(f"[Error] An unexpected error occurred: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                # 确保浏览器进程已关闭
                time.sleep(5)  # 等待短暂时间以确保浏览器进程退出
                for proc in psutil.process_iter(attrs=['pid', 'name']):
                    if 'chrome' in proc.info['name'].lower() or 'google' in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait()
            except Exception as e:
                print(f"[Error] An error occurred while quitting the driver: {e}")

    return page_content


def parse_character_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    character_dict = {"basic_info": {},  # 基础信息
                      "ascend": {
                          "ascend_material": {},
                      },  # 角色突破
                      "recommended_equipment": {
                          "weapon": {},  # 武器推荐
                          "artifact": {}  # 圣遗物推荐
                      },  # 推荐装备
                      "recommended_game_guide": {},  # 推荐攻略
                      "talents": {},  # 天赋
                      "constellation": {},  # 命之座
                      "specialty": {},  # 特殊料理
                      "character_CV": {},  # 角色CV
                      "more_description": None,  # 更多描述
                      "character_details": None,  # 角色详细信息
                      "character_story1": None,  # 角色故事1
                      "character_story2": None,  # 角色故事2
                      "character_story3": None,  # 角色故事3
                      "character_story4": None,  # 角色故事4
                      "character_story5": None,  # 角色故事5
                      "special_story": None,  # 特殊故事
                      "vision": {},  # 神之眼
                      "birthday_letter": None,  # 生日
                      "voices": {}  # 角色语音
                      }

    # deal with basic info
    def deal_basic_info():
        basic_info = soup.find('div', class_='obc-tmp-character__box')
        character_dict['basic_info']['name'] = basic_info.find('p', class_="obc-tmp-character__box--title").text
        character_dict['basic_info']['rank'] = len(basic_info.find('div', class_='obc-tmp-character__box--stars'))
        temp_keys = basic_info.select('div.obc-tmp-character__property div.obc-tmp-character__key')
        temp_values = basic_info.select('div.obc-tmp-character__property div.obc-tmp-character__value')
        for i in range(6):
            character_dict['basic_info']["".join(temp_keys[i].text.split())] = "".join(temp_values[i].text.split())

    # deal with ascend
    def deal_ascend():
        materials = soup.select('div#module-139 .swiper-wrapper .swiper-slide')
        for i in range(8):
            material = materials[i].select('table tbody tr ul li')
            if i == 0:
                temp = {}
                for ii in range(len(material)):
                    temp[material[ii].select_one('a span').text.strip()] = int(
                        material[ii].select_one('.obc-tmpl__icon-num').text.strip().strip("*"))
                character_dict['ascend']['ascend_material']["1级突破材料"] = temp
            elif 0 < i < 7:
                temp = {}
                for ii in range(len(material)):
                    temp[material[ii].select_one('a span').text.strip()] = int(
                        material[ii].select_one('.obc-tmpl__icon-num').text.strip().strip("*"))
                character_dict['ascend']['ascend_material'][f"{(i + 1) * 10}级突破材料"] = temp
            else:
                character_dict['ascend']['ascend_material']["90级突破材料"] = "无"
        # ToDo 1.每次突破的属性 2.重构

    def deal_recommended_equipment():
        recommended_equipment_weapon = soup.select(
            '#module-140 .obc-tmpl-x-scroll.swiper-slide.swiper-slide-active table tbody tr')
        for i in range(len(recommended_equipment_weapon)):
            if recommended_equipment_weapon[i].select('td')[0].select_one('p').text.strip() == '备注':
                pass
            else:
                character_dict['recommended_equipment']['weapon'][
                    recommended_equipment_weapon[i].select('td')[0].select_one('p a span').text] = \
                    recommended_equipment_weapon[i].select('td')[1].select_one('p').text

        recommended_equipment_artifact = soup.select(
            '#module-140 .obc-tmpl-x-scroll.swiper-slide.swiper-slide-next table tbody tr')
        for i in range(len(recommended_equipment_artifact)):
            character_dict['recommended_equipment']['artifact'][
                "/".join(artifact.text.strip() for artifact in
                         recommended_equipment_artifact[i].select('td')[0].select('p'))] = \
                recommended_equipment_artifact[i].select('td')[1].select_one('p').text
        # ToDo 1.武器栏中的备注

    def deal_recommended_game_guide():
        game_guide = soup.select('#module-142 .obc-tmpl-strategy__pc .obc-tmpl-strategy__card')
        for i in range(len(game_guide)):
            character_dict['recommended_game_guide'][
                game_guide[i].select_one('.obc-tmpl-strategy__card--text').text.strip()] = \
                game_guide[i].select_one('a').get('href')
        # ToDo 1.攻略帖子

    def deal_talents():
        talents = soup.select('div#module-143 .swiper-wrapper .swiper-slide')
        for i in range(len(talents)):
            character_dict['talents'][talents[i].select_one('.obc-tmpl__icon-text').text.strip()] = \
                talents[i].select_one('.obc-tmpl__paragraph-box.obc-tmpl__pre-text').text.strip()
        # ToDo 1.天赋名 2.详细属性

    def deal_constellation():
        constellation = soup.select('#module-144 .obc-tmpl-x-box table tbody tr')
        flag = len(constellation)
        if flag == 0:
            print('No constellation')
        else:
            for i in range(flag):
                character_dict['constellation'][constellation[i].select('td')[0].text] = constellation[i].select('td')[
                    1].text

    def deal_specialty():
        specialty = soup.select_one('#module-149 .obc-tmpl__paragraph-box')
        character_dict['specialty'][specialty.select_one('p a').text] = specialty.select('p')[1].text
        # ToDo 1.无料理情况

    def deal_character_CV():
        character_CV = soup.select_one('#module-150 .obc-tmpl__paragraph-box')
        for i in range(4):
            character_dict['character_CV'][character_CV.select('p')[i].text.split('：')[0]] = \
                character_CV.select('p')[i].text.split('：')[1]

    def deal_more_description():
        more_description = soup.select_one('#module-151 .obc-tmpl__paragraph-box')
        character_dict['more_description'] = " ".join(description.text for description in more_description.select('p'))

    def deal_character_details():
        character_details = soup.select_one('#module-152 .obc-tmpl__paragraph-box')
        character_dict['character_details'] = " ".join(detail.text for detail in character_details.select('p'))

    def deal_character_story1():
        character_story1 = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                2]
        character_dict['character_story1'] = " ".join(story.text for story in character_story1.select('p'))

    def deal_character_story2():
        character_story2 = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                3]
        character_dict['character_story2'] = " ".join(story.text for story in character_story2.select('p'))

    def deal_character_story3():
        character_story3 = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                4]
        character_dict['character_story3'] = " ".join(story.text for story in character_story3.select('p'))

    def deal_character_story4():
        character_story4 = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                5]
        character_dict['character_story4'] = " ".join(story.text for story in character_story4.select('p'))

    def deal_character_story5():
        character_story5 = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                6]
        character_dict['character_story5'] = " ".join(story.text for story in character_story5.select('p'))

    def deal_special_story():
        special_story = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                7]
        character_dict['special_story'] = " ".join(story.text for story in special_story.select('p'))

    def deal_vision():
        vision = \
            soup.find('div', id='module-group-98').find_all('div',
                                                            class_='obc-tmpl-part-wrap obc-tmpl-part--align-banner')[
                8]
        character_dict['vision'] = " ".join(story.text for story in vision.select('p'))

    def deal_voices():
        voices = soup.select_one('#module-153').select_one('[data-index="0"]').select('table tbody tr')
        for i in range(len(voices)):
            character_dict['voices'][voices[i].select('td')[0].text.strip()] = voices[i].select('td')[1].text.strip()

    deal_basic_info()
    deal_ascend()
    deal_recommended_equipment()
    deal_recommended_game_guide()
    deal_talents()
    deal_constellation()
    deal_specialty()
    deal_character_CV()
    deal_more_description()
    deal_character_details()
    deal_character_story1()
    deal_character_story2()
    deal_character_story3()
    deal_character_story4()
    deal_character_story5()
    deal_special_story()
    deal_vision()
    deal_voices()
    # ToDo 1.没有异常捕获
    return character_dict


def load_urls(filename):
    with open(f"{filename}", 'r', encoding='utf-8') as f:
        urls = f.readlines()
    return [url.strip() for url in urls]


def write_to_json(filename, content, folder='data'):
    with open(f"{folder}/{filename}", 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


def main():
    urls = load_urls('character_links.txt')
    total = len(urls)
    for url in urls:
        response = fetch_page(url, headless=True)
        character = parse_character_page(response)
        write_to_json(f'mohiyo-&原神-{character["basic_info"]["name"]}.json', character)
        print(f"Processed {urls.index(url) + 1}/{total} characters, url: {url}")


# response = fetch_page("https://bbs.mihoyo.com/ys/obc/content/4081/detail?bbs_presentation_style=no_header",
#                       headless=True)
# character = parse_character_page(response)
# write_to_json(f'mohiyo-&原神-{character["basic_info"]["name"]}.json', character)

if __name__ == '__main__':
    main()
