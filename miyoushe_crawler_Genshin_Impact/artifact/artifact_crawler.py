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


def parse_artifact_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    artifact_dict = {
        "basic_info": {
            "name": None,
            "稀有度": None,
            "获取途径": None,
            "2件套效果": None,
            "4件套效果": None,
        },
        "生之花" :{

        }



    }
    # ToDo 1.解析函数未完成

def load_artifact_links(filename='artifact_links.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        urls = list(data.values())
    return urls


def write_to_json(filename, content, folder='data'):
    with open(f"{folder}/{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
