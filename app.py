from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
import pandas as pd
import traceback
import fasttext

from lib_summary import summary


application = Flask(__name__)  # Change assignment here

global model
model = fasttext.load_model("./models/model.bin")
global message_example
with open('./models/message_example.json') as json_file:
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
        print(f"post_id:{m['post_id']} , sentiment:{model.predict(m['title'][0][0])} , proba:{model.predict(m['title'][1][0])}")
    
    return "Hello World!"


# тестовый прогон модели
@application.route("/new-news" , methods=['GET', 'POST'])  
def new_news():
    global model
    
    response = {'post_id':None,'summary':None,'sentiment':None,'proba':None,'url':None}
    
    try:
        #0 - load input data
        json_news = json.loads(request.get_data())
        print('1: ', json_news)
        
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
            
        print('2: ', response)
        
        #2 - make summary
        if response['post_id']:  
            url = response['url']
            url_main_text = summary.url_summary(url)
            response['summary'] = url_main_text['summary']
            
            
        print('3: ', response)
        
    except:
        #тест - для тестирования
        traceback.print_exc()
        return "!", 200
        
    #for heroku
    response = json.dumps(response)
    return str(response)  , 200

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

