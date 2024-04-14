import re

import jieba
import tokenizer
from transformers import AutoTokenizer, AutoModel
import torch

def split_text_to_chunks(text, max_length):
    chunks = []
    current_chunk = ""
    for char in text:
        current_chunk += char
        if len(current_chunk) >= max_length:
            last_natural_break = max(current_chunk.rfind(" "), current_chunk.rfind("。"), current_chunk.rfind("."), current_chunk.rfind("，"), current_chunk.rfind(","), current_chunk.rfind("（"), current_chunk.rfind("("))
            if last_natural_break > 0:
                chunks.append(current_chunk[:last_natural_break + 1])
                current_chunk = current_chunk[last_natural_break + 1:]
            else:
                chunks.append(current_chunk)
                current_chunk = ""
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def remove_special_characters(text):
    pattern = re.compile(r'[^\w\u4e00-\u9fa5,.!?;:\'\"、，。？！；：“”‘’《》（）【】]')
    return re.sub(pattern, '', text)

def Tokenizer(text):
    text_cut = "".join(jieba.cut(text))
    
    inputs = tokenizer(text_cut, return_tensors="pt",
                    padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(1)

    embeddings = embeddings.detach().tolist()
    return embeddings

tokenizer = AutoTokenizer.from_pretrained('../all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('../all-MiniLM-L6-v2', )