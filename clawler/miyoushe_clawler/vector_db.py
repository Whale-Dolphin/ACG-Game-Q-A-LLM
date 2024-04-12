import json
import os

from pymilvus import MilvusClient

from config import *

import os

def Zilliz_Upload(data_path):
    COLLECTION_NAME = 'miyouoshe_guide'
    client = MilvusClient(
        uri=CLUSTER_ENDPOINT, # Cluster endpoint obtained from the console
        token=ZILLIZ_TOKEN # API key or a colon-separated cluster username and password
    )

    with open(data_path, 'r') as f:
        data = json.load(f)
    
    for i in data:
        i['post_id'] = int(i['post_id'])

        res = client.insert(
            collection_name = COLLECTION_NAME,
            data = {
                'id': i['post_id'],
                'game_id': i['game_id'],
                'f_forum_id': i['f_forum_id'],
                'subject': i['subject'],
                'url': i['url'],
                'text': i['text'],
                'created_at': i['created_at'],
                'like_num': i['like_num'],
                'length': i['length'],
                'vector': i['vector'][0]
            }
        )