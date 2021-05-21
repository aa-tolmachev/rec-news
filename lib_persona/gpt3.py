import nltk

nltk.download('punkt')

from nltk.tokenize import sent_tokenize
import requests
from lib_cleaner import cleaner

import os
from lib_log import simple_log
global module_name
module_name = os.path.basename(__file__) #module name file

# ограничение по длине комментария
def get_few_sentences(sentences, max_len=100):
    text_length = 0
    res = ''
    for sentence in sentences:
        if ', -' in sentence:
            sentence = sentence[:sentence.find(', -')]
        if (len(res) + len(sentence) >= max_len):
            break
        text_length += len(sentence)
        res += sentence
    return res

# достаем коммент из затравки через api gpt3
def get_comment(text):
    url = 'https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict'
    start_word = 'Новость: '
    end_word = '. Я думаю, что '

    seed = start_word + text + end_word

    params = {
        'text': seed
    }

    req = requests.post(url, json=params).json()
    res = req['predictions']
    start_index = len(seed)
    tokens = sent_tokenize(res[start_index:], language='russian')
    clean_tokens = cleaner.sub_html_symb(tokens)
    comment = get_few_sentences(clean_tokens).capitalize()
    comment = comment.replace("\n", "")
    comment = comment.replace("\t", "")

    return comment

def get_news_with_comment(text):
    step = 0

    # делаем пять попыток сгенерировать коммент
    for _ in range(5):
        comment = get_comment(text)
        if comment != '':
            text = comment + '\n\n' + text
            break

    step = simple_log.make_log('end', module_name, step, message=f'first persona sentence added')

    return text



