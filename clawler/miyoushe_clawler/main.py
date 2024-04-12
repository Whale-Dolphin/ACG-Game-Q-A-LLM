import os
import json
import multiprocessing
from functools import partial

from tqdm import tqdm
from p_tqdm import p_map
import torch

from config import *
from clawer import Clawler
from text2vec import *
from utils import *
from vector_db import *

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

def Update_db():
    folder_path = 'data'
    files = os.listdir(folder_path)
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            Zilliz_Upload(file_path)   

# 多线程爬虫

# def worker(i):
#     post_id = maxn - i
#     proxy_info = proxy_list[i % len(proxy_list)]
#     target = Clawler(post_id, f_forum_id, proxy_info = proxy_info)
#     if target is not None:
#         data = target.__dict__
#         return data
#     return None

# def Write_Json(data_list, file_index, indices):
#     results = p_map(worker, indices, num_cpus=5)
    
#     for result in results:
#         if result is not None:
#             text = remove_special_characters(result.text)
#             chunks = split_text_to_chunks(text, 512)
#             cut_text = []
#             for j, i in enumerate(chunks):
#                 post_id = result.post_id + str(j).zfill(2)
#                 data = Vector_Paragraph(result.game_id, post_id, result.f_forum_id, result.subject, result.url, i, result.created_at, result.like_num, len(i), Tokenizer(i))
#                 cut_text.append(data.__dict__)
#             for i in cut_text:
#                 data_list.append(i)

#         while(data_list):
#             if len(data_list) >= 200:
#                 file_name = f"data/data_{file_index}.json"  
#                 file_index += 1
#                 with open(file_name, 'w') as f:
#                     json.dump(data_list[:200], f)
#                 data_list = data_list[200:]

#     if data_list:
#         file_name = f"data/data_{file_index}.json"
#         with open(file_name, 'w') as f:
#             json.dump(data_list, f)

# def main():
#     data_list = []
#     file_index = 0
#     div_num = 10
#     div_iterations = total_iterations // div_num
#     for i in range(div_num):
#         indices = list(range(i * div_iterations, i * div_iterations + div_iterations))
#         Write_Json(data_list, file_index, indices)

def fetch_and_process_post(i, proxy_list, maxn, f_forum_id):
    post_id = maxn - i
    proxy_info = proxy_list[i % len(proxy_list)]
    target = Clawler(post_id, f_forum_id, proxy_info=proxy_info)
    if target:
        return target.__dict__
    return None

def process_data_and_write(results, data_list, file_index):
    for result in results:
        if not result:
            continue
        text = remove_special_characters(result['text'])
        chunks = split_text_to_chunks(text, 512)
        
        for j, chunk in enumerate(chunks):
            post_id = f"{result['post_id']}{str(j).zfill(2)}"
            data = Vector_Paragraph(result['game_id'], post_id, result['f_forum_id'], result['subject'], result['url'], chunk, result['created_at'], result['like_num'], len(chunk), Tokenizer(chunk))
            data_list.append(data.__dict__)
        
        while len(data_list) >= 200:
            write_to_file(data_list[:200], file_index)
            data_list = data_list[200:]
            file_index += 1
            
    if data_list:
        write_to_file(data_list, file_index)

    return file_index + 1

def write_to_file(data, file_index):
    file_name = f"data/data_{file_index}.json"
    with open(file_name, 'w') as f:
        json.dump(data, f)

def main():
    data_list = []
    file_index = 0

    div_num = 10
    div_iterations = total_iterations // div_num
    for i in range(div_num):
        indices = range(i * div_iterations, (i + 1) * div_iterations)
        results = p_map(lambda x: fetch_and_process_post(x, proxy_list, maxn, f_forum_id), indices, num_cpus=5)
        file_index = process_data_and_write(results, data_list, file_index)

# 单线程爬虫

# def main():
#     Write_Json()

#     folder_path = 'data'
#     files = os.listdir(folder_path)
#     for file_name in files:
#         file_path = os.path.join(folder_path, file_name)
#         if os.path.isfile(file_path):
#             Zilliz_Upload(file_path)    

if __name__ == "__main__":
    main()