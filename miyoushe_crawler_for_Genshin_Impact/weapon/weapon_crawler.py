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


def parse_weapon_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    weapon_dict = {
        "basic_info": {
            "name": None,  # 名称
            "type": None,  # 装备类型
            "rank": None  # 星级
        },
        "equipment_description": {
            "refinement": None,  # 精炼
            "description": None,  # 描述
            "adventure_rank_limit": None,  # 冒险等阶限制
            "way_to_get": None  # 获取途径
        },
        "growth_value": {},  # 成长数值
        "related_story": None  # 相关故事
        # ToDo 1.推荐角色
    }

    def deal_basic_info():
        basic_info = soup.select('div#module-1187 table tbody tr')
        # name
        weapon_dict['basic_info']['name'] = basic_info[0].select('td')[1].text.replace("\n", "").split("：")[1].strip()
        # type
        weapon_dict['basic_info']['type'] = basic_info[1].select_one('td').text.replace("\n", "").split("：")[1].strip()
        # rank
        weapon_dict['basic_info']['rank'] = len(basic_info[2].select('i.obc-tmpl__rate-icon'))

    def deal_equipment_description():
        equipment_description = soup.select('div#module-1188 table tbody tr')
        flag = len(equipment_description)

        # refinement
        temp = equipment_description[0].select('p')[1].get_text()
        if temp:
            weapon_dict['equipment_description'][
                'refinement'] = f"{equipment_description[0].select('p')[0].get_text()} {temp}"

        # description
        temp = equipment_description[0].select('p')[-1].get_text()
        if temp:
            weapon_dict['equipment_description']['description'] = temp
        else:
            weapon_dict['equipment_description']['description'] = equipment_description[0].select('p')[-2].get_text()

        # adventure_rank_limit
        if flag == 3:
            weapon_dict['equipment_description']['adventure_rank_limit'] = equipment_description[1].select('p')[
                2].get_text()

        # way_to_get
        weapon_dict['equipment_description']['way_to_get'] = equipment_description[-1].select('p')[2].get_text()

    def deal_growth_value():
        levels = ['1级', '20级', '40级', '50级', '60级', '70级', '80级', '90级']
        growth_value = soup.select('div#module-1189 div.swiper-wrapper div.swiper-slide')
        for i in range(len(growth_value)):
            ascend_material = {}  # 突破材料
            data = {
                "initial_base_value": {},  # 初始基础数值
                "average_increase_per_level": {}  # 平均每级提升
            }  # 成长数值
            # ascend_material
            # Todo 1.某材料为空的判断逻辑 2.无突破材料的判断逻辑
            if len(growth_value[i].select('table')) > 1:
                material = growth_value[i].select('table')[1].select('tbody tr')
                for ii in range(len(material)):
                    ascend_material[material[ii].select('td')[-2].select_one('a').get_text(strip=True)] = \
                        material[ii].select('td')[-2].select_one('span.obc-tmpl__icon-num').get_text(
                            strip=True).replace(
                            "*",
                            "")
                    if material[ii].select('td')[-1].text != '':
                        ascend_material[material[ii].select('td')[-1].select_one('a').get_text(strip=True)] = \
                            material[ii].select('td')[-2].select_one('span.obc-tmpl__icon-num').get_text(
                                strip=True).replace(
                                "*",
                                "")
            else:
                ascend_material = "无"
            # initial_base_value
            initial_base_value = growth_value[i].select('table')[0].select('tbody tr td')[0].select('p')
            for ii in range(len(initial_base_value)):
                temp = initial_base_value[ii].get_text().split(":")
                data['initial_base_value'][temp[0]] = temp[1].strip()
            # average_increase_per_level
            average_increase_per_level = growth_value[i].select('table')[0].select('tbody tr td')[1].select('p')
            for ii in range(len(average_increase_per_level)):
                temp = average_increase_per_level[ii].get_text()
                if temp != '':
                    temp = temp.split(":")
                    data['average_increase_per_level'][temp[0]] = temp[1].strip()
                else:
                    data['average_increase_per_level'] = "无"

            # init_current_growth_value_dict
            current_growth_value_dict = {
                'ascend_material': ascend_material,
                'data': data
            }
            weapon_dict['growth_value'][levels[i]] = current_growth_value_dict
        # Todo 数据格式有待改进

    def deal_related_story():
        related_story = soup.select_one('div#module-1190 div.obc-tmpl__paragraph-box')
        if related_story:
            weapon_dict['related_story'] = related_story.get_text().strip()
            # Todo 没有保存文字的分段
        else:
            weapon_dict['related_story'] = None

    deal_basic_info()
    deal_equipment_description()
    deal_growth_value()
    deal_related_story()

    return weapon_dict


def load_weapon_links(filename='weapon_links.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        urls = list(data.values())
    return urls


def write_to_json(filename, content, folder='data'):
    with open(f"{folder}/{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


def main():
    urls = load_weapon_links()
    total = len(urls)
    for url in urls:
        try:
            html = fetch_page(url)
            weapon_dict = parse_weapon_page(html)
            write_to_json(f"mohiyo-&原神-武器-{weapon_dict['basic_info']['name']}", weapon_dict)
            print(f"[Info] Successfully processed {urls.index(url) + 1}/{total} weapon, url: {url}")
        except Exception as e:
            print(f"[Error] An error occurred while processing {url}: {e}")
            continue


if __name__ == '__main__':
    main()
