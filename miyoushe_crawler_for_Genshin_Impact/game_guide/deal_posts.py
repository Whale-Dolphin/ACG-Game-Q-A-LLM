import os
import json
import time


def delete_invalid_json_files(folder_path, required_forum_id, min_like_num):
    """
    遍历指定文件夹下的所有 JSON 文件，删除数据不符合要求的文件。

    :param folder_path: JSON 文件所在的文件夹路径
    :param required_forum_id: 需要的 f_forum_id
    :param min_like_num: 最小的 like_num
    """
    if not os.path.exists(folder_path):
        print(f"[Error] Folder {folder_path} does not exist.")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            try:
                # 确保文件在读取后正确关闭
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # 关闭文件后再进行删除操作
                if data.get('f_forum_id') != required_forum_id or data.get('like_num') < min_like_num:
                    print(f"[Delete] Deleting invalid file: {filename}")

                    # 尝试删除文件，添加重试机制
                    retry_count = 0
                    max_retries = 5
                    while retry_count < max_retries:
                        try:
                            os.remove(file_path)
                            print(f"[Success] Deleted file: {filename}")
                            break
                        except PermissionError:
                            print(f"[Retry] File {filename} is in use, retrying... ({retry_count + 1}/{max_retries})")
                            time.sleep(1)  # 等待1秒钟再重试
                            retry_count += 1
                    else:
                        print(f"[Failed] Could not delete file after {max_retries} retries: {filename}")

            except json.JSONDecodeError:
                print(f"[Error] Failed to decode JSON in file: {filename}")
            except Exception as e:
                print(f"[Error] An error occurred while processing file {filename}: {e}")


# 使用示例
folder_path = 'data'  # 指定你的文件夹路径
required_forum_id = 43
min_like_num = 50

delete_invalid_json_files(folder_path, required_forum_id, min_like_num)
