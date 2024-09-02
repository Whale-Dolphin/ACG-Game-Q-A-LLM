from fake_useragent import UserAgent
import requests

def generate_fake_ua():
    ua = UserAgent()
    return ua.random

def write_links_to_file(links, file_path=''):
    with open(file_path, 'a', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

def fetch_data(url, headers, input_id=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功（状态码200）
        response_json = response.json()  # 返回JSON格式的数据

        # 检查返回的JSON数据是否为空
        if response_json.get('data') is None:
            print(f"Failed to fetch data: empty response, input_id: {input_id}")
            return None

        return response_json
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}, input_id: {input_id}")
    except Exception as err:
        print(f"Other error occurred: {err}, input_id: {input_id}")
    return None

def extract_post_ids(data, url_type, min_view_num=0, min_like_num=50, min_reply_num=0):
    post_ids = []
    if url_type == 'last_id':
        flag='list'
    else:
        flag='posts'

    if data and "data" in data and flag in data["data"]:
        for item in data["data"][flag]:
            post_id = item.get("post", {}).get("post_id")
            stat = item.get("stat", {})

            view_num = stat.get("view_num", 0)
            like_num = stat.get("like_num", 0)
            reply_num = stat.get("reply_num", 0)

            if (post_id and
                view_num >= min_view_num and
                like_num >= min_like_num and
                reply_num >= min_reply_num):
                post_ids.append(post_id)
    return post_ids

def main():
    # Choose the URL type you want to crawl
    # url_type = 'offset'  # 可选项：'last_id'(最新回复) 或 'offset'（热门）
    url_type = 'last_id'


    if url_type == 'last_id':
        url_template = 'https://bbs-api.miyoushe.com/post/wapi/getForumPostList?forum_id=43&gids=2&is_good=false&is_hot=false&page_size=20&sort_type=1'
    elif url_type == 'offset':
        url_template = 'https://bbs-api.miyoushe.com/post/wapi/recommendWalkthrough?forum_id=43&gids=2&is_good=false&is_hot=true&size=20'
    else:
        raise ValueError("Invalid url_type. Choose 'last_id' or 'offset'.")

    headers = {
        'Referer': 'https://www.miyoushe.com/',
        'User-Agent': generate_fake_ua()
    }

    last_id = None
    offset = 1  # 初始 offset 为 1
    all_post_ids = []

    max_iterations = 5000  # 设置要抓取的最大次数
    iteration_count = 0

    while iteration_count < max_iterations:
        if url_type == 'last_id' and last_id:
            url = f"{url_template}&last_id={last_id}"
        elif url_type == 'offset' and offset > 1:
            url = f"{url_template}&offset={offset}"
        else:
            url = url_template

        data = fetch_data(url, headers, input_id=last_id or offset)
        if not data:
            break

        # 调整过滤条件
        post_ids = extract_post_ids(data, url_type)
        if post_ids:
            all_post_ids.extend(post_ids)
            write_links_to_file(post_ids)  # 保存每次获取的链接
            if url_type == 'last_id':
                last_id = data["data"].get("last_id")
            else:
                offset += 1  # 更新 offset
        else:
            print("No more posts found.")
            break

        if data["data"].get("is_last"):
            print("Reached the last page.")
            break

        iteration_count += 1
        print(f"Iteration {iteration_count} complete.")

    print(f"Total post IDs collected: {len(all_post_ids)}")

if __name__ == "__main__":
    main()
