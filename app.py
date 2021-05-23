from flask import Flask
from flask import request
import requests
from flask import make_response
import os
from io import StringIO
import json
import pandas as pd
import traceback
import fasttext

from lib_summary import summary
from lib_cleaner import cleaner
from lib_persona import gpt3
# from lib_persona import persona

from lib_log import simple_log
global module_name
module_name = os.path.basename(__file__) #module name file




application = Flask(__name__)  # Change assignment here

global model
model = fasttext.load_model("./models/model.bin")
global message_example
with open('./models/message_example.json', encoding='utf-8') as json_file:
    message_example = json.load(json_file)

# тестовый вывод
@application.route("/")  
def hello():
    return "Hello World!"


# тестовый прогон модели
@application.route("/test")  
def test():
    global message_example
    global model

    
    for m in message_example['articles']:
        print(
            f"post_id:{m['post_id']} , "
            f"sentiment:{model.predict(m['title'][0][0])} ,"
            f" proba:{model.predict(m['title'][1][0])}"
        )
    
    return "Hello World!"


# тестовый прогон модели
@application.route("/new-news" , methods=['GET', 'POST'])  
def new_news():
    global model
    global module_name
    step = 0
    
    response = {'post_id':None,'summary':None,'sentiment':None,'proba':None,'url':None}
    
    try:
        #0 - load input data
        json_news = json.loads(request.get_data())
        step = simple_log.make_log('i',module_name , step, message=response )
        
        #1 - find most positive news
        df = pd.DataFrame()
        for n in json_news['articles']:
            post_id = n['post_id']
            url = n['url']
            title = n['title']

            m_predict = model.predict(n['title'])
            sentiment = m_predict[0][0]
            proba = m_predict[1][0]


            df = df.append({'post_id': post_id,'sentiment': sentiment.replace('__label__',''), 'proba':proba , 'url':url}, ignore_index=True)
        

        df = df[(df['sentiment'] != 'negative')][:]

        if df.shape[0] > 0:

            if 'positive' in df['sentiment'].unique():
                df = df[(df['sentiment'] == 'positive')][:]

            most_positive = df.sort_values(by = ['proba'] , axis = 0 , ascending = False).iloc[0]
            response['post_id'] = most_positive['post_id']
            response['proba'] = most_positive['proba']
            response['sentiment'] = most_positive['sentiment']
            response['url'] = most_positive['url']
            
        step = simple_log.make_log('i',module_name , step, message=response )
        
        #2 - make summary
        if response['post_id']:  
            url = response['url']
            url_main_text = summary.url_summary(url)
            response['summary'] = url_main_text['summary']

            #3 - clean summary
            clean_summary = cleaner.fresh_text(url_main_text['summary'])
            response['summary'] = clean_summary
            
            #4 - add persona sentence
            # persona_clean_summary = persona.add_persona_first_sentence(clean_summary)
            #response['summary'] = persona_clean_summary
            gpt3_clean_summury = gpt3.get_news_with_comment(clean_summary)
            response['summary'] = gpt3_clean_summury
            
            
        step = simple_log.make_log('i',module_name , step, message=response )
        
    except:
        #log error
        step = simple_log.make_log('e',module_name , step, message=response )
        #тест - для тестирования
        traceback.print_exc()
        error_message = '!'
        if json_news.get('debug'):
            exception_buffer = StringIO()
            traceback.print_exc(file=exception_buffer)
            exception_buffer.seek(0)
            error_message =  exception_buffer.read()

        return error_message, 500
        
    #for heroku
    response = json.dumps(response)
    return str(response)  , 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

