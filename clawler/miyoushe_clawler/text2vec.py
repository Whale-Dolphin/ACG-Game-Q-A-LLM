import re

import jieba
import tokenizer
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese')

def split_text(text, words_per_segment=100, char_offset=50):
    words = text.split()
    
    segments = []
    current_position = 0
    while current_position < len(words):
        end_position = min(current_position + words_per_segment, len(words))
        
        segment = ' '.join(words[current_position:end_position])
        segments.append(segment)
        
        if current_position + words_per_segment < len(words):
            next_start = ' '.join(words[:current_position + words_per_segment]).rfind(' ', 0, char_offset)
            current_position += len(' '.join(words[current_position:current_position + words_per_segment][:next_start]).split())
        else:
            break

    return segments

def remove_special_characters(text):
    pattern = re.compile(r'[^\w\u4e00-\u9fa5]')
    return re.sub(pattern, '', text)

def Tokenizer(text):
    text_cut = "".join(jieba.cut(text))

    

    inputs = tokenizer(text_cut, return_tensors="pt",
                    padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(1)

    return embeddings
