import json

from pymilvus import MilvusClient

from utils import *

def Zilliz_Upload(data):
    client = MilvusClient(
        # Cluster endpoint obtained from the console
        uri="Your Milvus cluster endpoint",
        # API key or a colon-separated cluster username and password
        token="Your Milvus API key",
    )

    res = client.insert(
        collection_name = "miyoushe_articles",
        data = data
    )