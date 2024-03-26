import os
import json
import multiprocessing
from functools import partial

from tqdm import tqdm
from p_tqdm import p_map
import torch

from config import *
from clawer import Clawler
from text2vec import Tokenizer
from utils import *
from zilliz import Zilliz_Upload

# 多线程爬虫
# def worker(i):
#     post_id = maxn - i
#     print(f"Processing post_id: {post_id}")
#     proxy_info = proxy_list[i % len(proxy_list)]
#     target = Clawler(post_id, f_forum_id, True, proxy_info)
#     if target is not None:
#         data = target.__dict__
#         return data
#     return None

# def main():
#     indices = range(total_iterations)
#     results = p_map(worker, indices, num_cpus=5)
    
#     data_list = []
#     file_index = 0
    
#     for result in results:
#         if result is not None:
#             data_list.append(result)
#             if len(data_list) == 200:
#                 file_name = f"data/data_{file_index}.json"  
#                 file_index += 1
#                 with open(file_name, 'w') as f:
#                     json.dump(data_list, f)
#                 data_list.clear()

#     if data_list:
#         file_name = f"data/data_{file_index}.json"
#         with open(file_name, 'w') as f:
#             json.dump(data_list, f)

# 单线程爬虫
# def main():
#     data_index = []
#     file_index = 0
#     for i in tqdm(range(total_iterations)):
#         post_id = maxn - i

#         result = Clawler(post_id, f_forum_id)


#         if result is not None:
#             data_index.append(result.__dict__)

#         if len(data_index) == 200 or i == total_iterations - 1: 
#             file_name = f"data/data_{file_index}.json"
#             file_index += 1
#             with open(file_name, 'w') as f:
#                 json.dump(data_index, f)
#             data_index.clear() 

if __name__ == "__main__":
    main()