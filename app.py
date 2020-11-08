from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
import pandas as pd
import traceback
import fasttext


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
    
    response = {'post_id':None,'summary':'coming soon','sentiment':None,'proba':None}
    
    try:
        json_news = json.loads(request.get_data())
        print(json_news)
        
        df = pd.DataFrame()
        for n in json_news['articles']:
            post_id = n['post_id']
            title = n['title']

            m_predict = model.predict(n['title'])
            sentiment = m_predict[0][0]
            proba = m_predict[1][0]


            df = df.append({'post_id': post_id,'sentiment': sentiment.replace('__label__',''), 'proba':proba}, ignore_index=True)
        

        df = df[(df['sentiment'] != 'negative')][:]

        if df.shape[0] > 0:

            if 'positive' in df['sentiment'].unique():
                df = df[(df['sentiment'] == 'positive')][:]

            most_positive = df.sort_values(by = ['proba'] , axis = 0 , ascending = False).iloc[0]
            response['post_id'] = most_positive['post_id']
            response['proba'] = most_positive['proba']
            response['sentiment'] = most_positive['sentiment']

        print(response)
    except:
        #тест - для тестирования
        traceback.print_exc()
        return "!", 200
        
    return response

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0')

