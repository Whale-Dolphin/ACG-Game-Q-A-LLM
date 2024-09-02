from fake_useragent import UserAgent
import requests

def generate_fake_ua():
    ua = UserAgent()
    return ua.random

def write_links_to_file(links, file_path='filtered links.txt'):
    with open(file_path, 'a', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

def fetch_data(url, headers, input_id=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功（状态码200）
        response_json = response.json()  # 返回JSON格式的数据\
        # print(response_json)

        # 检查返回的JSON数据是否为空
        if response_json.get('data') is None:
            print(f"Failed to fetch data: empty response")
            return None

        return response_json
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}, input_id: {input_id}")
    except Exception as err:
        print(f"Other error occurred: {err}, input_id: {input_id}")
    return None




def extract_post_ids(data, min_view_num=0, min_like_num=50, min_reply_num=0):
    post_ids = []
    flag=False
    if data and "data" in data and "posts" in data["data"]:
        for item in data["data"]["posts"]:
            post_id = item.get("post", {}).get("post_id")
            if post_id:
                # print(post_id)
                flag=True
            f_forum_id = item.get("post", {}).get("f_forum_id")
            stat = item.get("stat", {})

            # print(f_forum_id)
            # print(post_id)

            view_num = stat.get("view_num", 0)
            like_num = stat.get("like_num", 0)
            reply_num = stat.get("reply_num", 0)

            if (post_id and
                f_forum_id == 43 and
                view_num >= min_view_num and
                like_num >= min_like_num and
                reply_num >= min_reply_num):
                post_ids.append(post_id)
    return flag,post_ids

def main():
    url_template = 'https://bbs-api.miyoushe.com/post/wapi/getTopicPostList?game_id=2&gids=2&list_type=0&page_size=20&topic_id=1858'
    headers = {
        'Referer': 'https://www.miyoushe.com/',
        'User-Agent': generate_fake_ua()
    }

    last_id = None
    all_post_ids = []

    max_iterations = 50000  # 设置要抓取的最大次数
    iteration_count = 0

    while iteration_count < max_iterations:
        if last_id:
            url = f"{url_template}&last_id={last_id}"
        else:
            url = url_template

        data = fetch_data(url, headers, input_id=last_id)
        if not data:
            break

        # 提取帖子ID
        flag,post_ids = extract_post_ids(data)
        print(flag,post_ids)
        if post_ids:
            all_post_ids.extend(post_ids)
            write_links_to_file(post_ids)  # 保存每次获取的链接
            last_id = data["data"].get("last_id")
        elif flag:
            print("No posts found.")
            last_id = data["data"].get("last_id")
        else:
            print("No more posts found.")
            break

        if data["data"].get("is_last"):
            print("Reached the last page.")
            break

        iteration_count += 1
        print(f"Iteration {iteration_count} complete.")
        print("-----------------------------------")

    print(f"Total post IDs collected: {len(all_post_ids)}")

if __name__ == "__main__":
    main()
# 4.8版本的最新帖子