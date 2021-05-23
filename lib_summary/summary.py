import requests
from bs4 import BeautifulSoup
import re
import traceback
import os
import random


from lib_log import simple_log
global module_name
module_name = os.path.basename(__file__) #module name file



def make_summary(text):
    smr_url = 'https://api.smrzr.io/v1/summarize?ratio=0.3'

    r = requests.post(smr_url, data=text.encode('utf-8'))

    summary_text = r.json()['summary']
    
    return summary_text

def content_main_text(soup):
    #generate total text
    #https://www.datacamp.com/community/tutorials/amazon-web-scraping-using-beautifulsoup?utm_source=adwords_ppc&utm_campaignid=1455363063&utm_adgroupid=65083631748&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=278443377086&utm_targetid=dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=1011994&gclid=CjwKCAiAnvj9BRA4EiwAuUMDf9ikPGhZRwqK5U8wa49ge0oa2GpDHoxjPJUgPNCdV1notYt8CxAcbBoCoM0QAvD_BwE
    title = ''
    meta = ''
    par = ''

    ###### title
    #title_arr = soup.findAll('title')
    title_arr = soup.findAll('meta' , attrs = {'name':'title'} )
    if title_arr:
        #title = title_arr[0].text
        title = title_arr[0].attrs['content']


    ##### meta
    meta_attr_dicts = [{'name':'description'},
                       {'property':'og:description'},
                       {'property':'twitter:descriptionn'} ,
                       {'itemprop':'description'}
                      ]
    for meta_attr_dict in meta_attr_dicts:
        meta_arr = soup.findAll('meta', attrs=meta_attr_dict)

        if meta_arr:
            for m in meta_arr:
                m_text = m.attrs['content']
                meta += m_text
                if '.' not in  meta[-3:]: 
                    meta += '.' 
                meta += '\n' 


    ####### paragraph
    par_arr = soup.findAll('p'  )[:5]
    if par_arr:
        for p in par_arr:
            par += p.text
            if '.' not in  par[-3:]: 
                par += '.' 
            par += '\n' 

    total_text = title + '.\n' + meta + '.\n' + par
    
    return total_text

def url_summary(url):
    global module_name
    step = 0
    
    url_main_text = {'summary':None}
    
    try:
        #0 - load content
        resp = requests.get(url)
        content = resp.text
        step = simple_log.make_log('i',module_name , step, message=f'load content - {len(content)}' )

        #1 - preprocess
        content = re.sub(r'<a.*>.*</a>', '', content)

        soup = BeautifulSoup(content)

        tags=soup.findAll("a")
        for tag in tags:
            tag.replaceWith('')

        step = simple_log.make_log('i',module_name , step, message=f'clean tags' )

        #2 - generate main text
        main_text = content_main_text(soup)

        step = simple_log.make_log('i',module_name , step, message=f'generate main text - {len(main_text)}' )

        #3 make summary
        summary_text = make_summary(main_text)
        url_main_text['summary'] = summary_text

        step = simple_log.make_log('end',module_name , step, message=f'len(summary_text) - {len(summary_text)}' )
    except:
        traceback.print_exc()
        
    return url_main_text



def add_link_to_news(summary: str, url:str) -> str:

    url_names = ['ссылка','источник','оригинал','новость',
                ,'линк','пруфы','докозательство','пруф','интересно'
                ]

    url_2nd = ['вот тут','взял отсюда','вот тут говорят','стырил отсюда','здесь оригинал','отсюда','вот отсюда',
                ,'вот ловите','цитирую отсюда','здесь прочитал','здесь говорят','отсюда узнал'
                ]


    url_name = random.choice(url_names)
    url_name = url_name + ', ' + random.choice(url_2nd)

    summary_with_hyperlink = summary + '\n\n'
    summary_with_hyperlink += f'<a href="{url}">{url_name}</a>'

    return summary_with_hyperlink




    