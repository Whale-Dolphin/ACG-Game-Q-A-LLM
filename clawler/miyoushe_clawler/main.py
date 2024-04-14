import os
import json
import multiprocessing
import logging
from functools import partial

from tqdm import tqdm
from p_tqdm import p_map
import torch

from config import *
from clawer import Clawler
from text2vec import *
from utils import *
from vector_db import *

os.environ["TOKENIZERS_PARALLELISM"] = "false"

log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_filename = "main.log"

logging.basicConfig(level=logging.INFO, format=log_format, filename=log_filename, filemode='a')

logger = logging.getLogger()

# def Write_Json():
#     data_index = []
#     file_index = 0
#     for i in tqdm(range(total_iterations)):
#         post_id = maxn - i

#         result = Clawler(post_id, f_forum_id)

#         if result is not None:
#             text = remove_special_characters(result.text)
#             chunks = split_text_to_chunks(text, 512)
#             cut_text = []
#             for j, i in enumerate(chunks):
#                 post_id = result.post_id + str(j).zfill(2)
#                 data = Vector_Paragraph(result.game_id, post_id, result.f_forum_id, result.subject, result.url, i, result.created_at, result.like_num, len(i), Tokenizer(i))
#                 cut_text.append(data.__dict__)
#             data_index.append(cut_text)

#         if len(data_index) == 200 or i == total_iterations - 1: 
#             file_name = f"data/data_{file_index}.json"
#             file_index += 1
#             with open(file_name, 'w') as f:
#                 json.dump(data_index, f)
#             data_index.clear()

# 单线程爬虫

# def main():
#     Write_Json()

#     folder_path = 'data'
#     files = os.listdir(folder_path)
#     for file_name in files:
#         file_path = os.path.join(folder_path, file_name)
#         if os.path.isfile(file_path):
#             Zilliz_Upload(file_path)    

def Update_db():
    folder_path = 'data'
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            Zilliz_Upload(file_path)   

def main():
    data_list = []
    file_index = 0

    div_num = 20
    div_iterations = total_iterations // div_num
    for i in range(div_num):
        indices = range(i * div_iterations, (i + 1) * div_iterations)
        results = p_map(lambda x: fetch_and_process_post(x, maxn, f_forum_id), indices, num_cpus=10)
        process_data_and_write(results, data_list, file_index)

def fetch_and_process_post(i, maxn, f_forum_id, proxy_list=None):
    try:
        post_id = maxn - i
        proxy_info = None
        if proxy_list is not None:
            proxy_info = proxy_list[i % len(proxy_list)]
        target = Clawler(post_id, f_forum_id, proxy_info=proxy_info)
        if target:
            return target.__dict__
    except Exception as e:
        logger.error(f"Error fetching post {post_id}: {e}")
    return None

def process_data_and_write(results, data_list, file_index):
    for result in results:
        if not result:
            continue
        logger.info(f"Processing post {result['post_id']}")
        text = remove_special_characters(result['text'])
        chunks = split_text_to_chunks(text, 512)

        for j, chunk in enumerate(chunks):
            post_id = f"{result['post_id']}{str(j).zfill(2)}"
            data = Vector_Paragraph(result['game_id'], post_id, result['f_forum_id'], result['subject'], result['url'], chunk, result['created_at'], result['like_num'], len(chunk), Tokenizer(chunk))
            data_list.append(data.__dict__)

        while len(data_list) >= 200:
            logger.info(f"Writing to file {file_index}")
            write_to_file(data_list[:200], file_index)
            data_list = data_list[200:]
            file_index += 1

    if data_list:
        write_to_file(data_list, file_index)

def write_to_file(data, file_index):
    file_name = f"data/data_{file_index}.json"
    with open(file_name, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    main()