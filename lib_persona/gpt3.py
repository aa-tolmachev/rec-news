import nltk
import time

from nltk.tokenize import sent_tokenize
import requests
from lib_cleaner import cleaner
from lib_formatter import formatter

import traceback
import os
from lib_log import simple_log
global module_name
module_name = os.path.basename(__file__) #module name file

# ограничение по длине комментария
def get_few_sentences(sentences, max_len=100):
    sentences_amount = 0
    total_length = 0
    for sentence in sentences:
        if (total_length + len(sentence) >= max_len):
            break
        else:
            total_length += len(sentence)
            sentences_amount += 1
    result = " ".join(sentences[:sentences_amount])
    return result

# достаем коммент из затравки через api gpt3
def get_comment(text):
    comment = ''
    url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
    start_word = 'Новость: '
    end_word = 'Я думаю, что '

    seed = start_word + text + end_word

    params = {
        'text': seed
    }
    req = requests.post(url, json=params)
    print(req)
    try:
        res = req.json()
        pred = res['predictions']
        start_index = len(seed)
        tokens = sent_tokenize(pred[start_index:], language='russian')
        print(tokens)
        comment = get_few_sentences(tokens)
    except:
        traceback.print_exc()

    return comment

def get_summary_with_comment(clean_summary, formatted_summary):
    step = 0

    # делаем несколько попыток сгенерировать коммент
    for _ in range(3):
        comment = get_comment(clean_summary)
        if comment:
            comment = cleaner.fresh_text(comment)
            comment = formatter.format_comment(comment)
            formatted_summary = formatted_summary + '\n\n' + '💬 ' + comment
            step = simple_log.make_log('end', module_name, step, message=f'added gpt3 generation')
            break
        time.sleep(1.5)


    return formatted_summary



