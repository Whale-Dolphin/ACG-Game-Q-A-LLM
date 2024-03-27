# 使用milvus在线库zilliz储存在云端
# import json

# from pymilvus import MilvusClient

# from config import *

# def Zilliz_Upload(data):
#     client = MilvusClient(
#         # Cluster endpoint obtained from the console
#         uri = zilliz_uri,
#         # API key or a colon-separated cluster username and password
#         token = zilliz_api,
#     )

#     res = client.insert(
#         collection_name = "miyoushe_articles",
#         data = data
#     )

# 使用langchain自带的Chroma储存在本地
