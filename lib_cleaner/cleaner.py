import re
import numpy as np
import collections

from numpy import dot
from numpy.linalg import norm
import traceback
import html

def make_sentences(text):
    sentences = re.split('\.\s',text)
    sentences = [s for s in sentences if len(s) > 5]
    return sentences

def clean_tech(sentences):
    sentences_new = []

    for s in sentences:
        
        s_new = re.sub(r'\:.*\:.*', '', s)
        s_new = re.sub(r'\W+$', '', s_new)
        s_new = re.sub(r'^\W+', '', s_new)
        s_new = re.sub(r'\|.*', '', s)
        s_new = re.sub(r'\@.*', '', s)
        
        s_new = re.sub(r'\{.*\}', '' ,  s)

        
        s_new = re.sub(r'\S+\.\w\w$', '.' ,  s)
        
        s_new = re.sub(r'\:.*\:.*', '.' ,  s)


        
        sentences_new.append(s_new)
        
    return sentences_new
        
        
def clean_duplicates(sentences):
    #make simple vector to calc similarity
    all_words = ' '.join(sentences).lower()
    all_words = all_words.replace(' ','')

    grams = []
    n = 3

    #find all grams
    for step in range(len(all_words)-n+1):
        gram = all_words[step:step+n]
        grams.append(gram)

    #calc frequency
    c = collections.Counter(grams)
    common_grams = c.most_common(20)
    common_grams = np.array(common_grams)[:,0]

    #similarities
    new_sentences = []
    for s , i in zip( sentences , range(len(sentences)) ):

        s_cur = s.lower().replace(' ','')
        s_prev_arr = sentences[:i]

        s_cur_emb = np.zeros(len(common_grams))
        for common_gram , cg_i in zip(common_grams, range(len(common_grams)) ):
            s_cur_emb[cg_i] = s_cur.count(common_gram)

        max_cos_sim = 0
        for s_prev in s_prev_arr:
            s_prev_emb = np.zeros(len(common_grams))
            for common_gram , cg_i in zip(common_grams, range(len(common_grams)) ):
                s_prev_emb[cg_i] = s_prev.count(common_gram)

            cos_sim = dot(s_cur_emb, s_prev_emb)/(norm(s_cur_emb)*norm(s_prev_emb))
            if cos_sim > max_cos_sim:
                max_cos_sim = cos_sim

        if max_cos_sim < 0.8:
            new_sentences.append(s)
    return new_sentences

def add_dots(sentences):
    new_sentences = []

    for s in sentences:
        s += '.'
        s = re.sub(r'\.+', '.', s)
        new_sentences.append(s)
        
    return new_sentences

def sub_html_symb(sentences): # Функция для очистки html спец. символов
    new_sentences = []
    for s in sentences:
        s = html.unescape(s.replace("&nbsp;", " ")).replace("\n", " ").replace("\r", "").replace("\xa0", " ").replace("\u202f", " ")
        new_sentences.append(s)
    return new_sentences   

def sub_html_text(s):
    return html.unescape(s.replace("&nbsp;", " ").replace("&nbsp; ", " ")).replace("\n", " ").replace("\r", "").replace("\xa0", " ").replace("\u202f", " ")

def interfaxdecode(sentences): # Кодировка интерафкса
    new_sentences = []
    if "È" in " ".join(sentences):
        for s in sentences:
            s = s.encode("windows-1252").decode("windows-1251")
            new_sentences.append(s)
    else:
        return sentences
    return new_sentences

def metalinkscleaner(sentences): # Очистка всякого говнища
    tempalltext = " ".join(sentences)
    if "Allhockey" in tempalltext:
        return ["", ""]
    if " - 7Дней.ру" in tempalltext:
        return ["", ""]
    if ":: РБК" in sentences[0]:
        sentences[0] = sentences[0].replace(sentences[0][sentences[0].find("::")-1:sentences[0].find(".", sentences[0].find("::"), len(sentences[0]))+1], "")
    if ": Lenta.ru" in sentences[0]:
        sentences[0] = sentences[0].replace(sentences[0][sentences[0].find(":"):sentences[0].find(".", sentences[0].find(":"), len(sentences[0])) + 3], "")
    if "Читайте подробнее" in sentences[0]:
        sentences[0] = sentences[0].replace(sentences[0][sentences[0].find(" -"):sentences[0].find(".", sentences[0].find(" -"), len(sentences[0]))], "")
    if " - МК" in sentences[0]:
        sentences[0] = sentences[0].replace(" - МК", "")
    if "поддержке Федерального агентства" in tempalltext:
        for i in range(len(sentences)):
            if "поддержке Федерального агентства" in sentences[i]:
                del(sentences[i])
                break
                
    if "|" in sentences[0]:
        tempsplit = sentences[0].split()
        for i in range(len(tempsplit)-1):
            if tempsplit[i] == "|":
                del(tempsplit[i+1])
                del(tempsplit[i])
                break
        sentences[0] = " ".join(tempsplit) + "."    
    if "РИА Новости," in tempalltext or "Новости в России и мире," in tempalltext:
        for i in range(len(sentences)):
            if "РИА Новости," in sentences[i]:
                sentences[i] = sentences[i].replace(sentences[i][sentences[i].find("РИА Новости,"):len(sentences[i])+1], "")
            if "Новости в России и мире," in sentences[i]:
                sentences[i] = sentences[i].replace(sentences[i][sentences[i].find("Новости в России и мире,"):len(sentences[i])+1], "")
            if "Фото и видео с места событий" in sentences[i]:
                sentences[i] = ""
    if "znak Новости," in sentences[-1]:
        sentences[-1] = sentences[-1].replace(sentences[-1][sentences[-1].find("znak Новости,"):len(sentences[-1])], "")
    if "/ Znak.com" in tempalltext:
        for i in range(len(sentences)):
            if "/ Znak.com" in sentences[i]:
                tempsent = sentences[i][::-1]
                tempsent = tempsent.replace(tempsent[tempsent.find("moc.kanZ"):tempsent.find(".", tempsent.find("moc.kanZ")+6, len(tempsent))], "")
                sentences[i] = tempsent[::-1][1:]
    if "/ТАСС/" in tempalltext:
        for i in range(len(sentences)):
            if "/ТАСС/" in sentences[i]:
                sentences[i] = sentences[i].replace("/ТАСС/.", "").replace("/ТАСС/", "")
        if len(sentences[0]) <= 2:
            del(sentences[0])
    if "©" in sentences[-1] or "Все права защищены" in sentences[-1] or "(c)" in sentences[-1] or "Copyright" in sentences[-1] or "Зарегистрировано Федеральной службой" in sentences[-1]:
        del(sentences[-1])
    if "Интерфакс: " in sentences[0]:
        sentences[0] = sentences[0].replace("Интерфакс: ", "")
    if "Фото:" in tempalltext:
        for i in range(len(sentences)):
            if "Фото:" in sentences[i]:
                sentences[i] = sentences[i].replace(sentences[i][sentences[i].find("Фото:"):len(sentences[i])], "")
    return sentences

def bayancleaner(sentences): # [...]
    if "[…]" in sentences[-1]:
        return sentences[:-1]
    else:
        return sentences

def links(sentences): # Ссылки в тексте
    tempjoin = " ".join(sentences)
    if "http" in tempjoin:
        for i in range(len(sentences)):
            if "http" in sentences[i]:
                sentences[i] = sentences[i].replace(sentences[i][sentences[i].find("http") : sentences[i].find(" ", sentences[i].find("http"), len(sentences[i])) + 1], "")

    return sentences

def russianlang(text): # Проверка, что новость содержит больше половины русских символов, а не странных кодировок, чтобы не проходило говно
    if len(text.replace(" ", "")):
        alph = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
        punc = set('''!()-[]{};?@#$%:'"\,./^&;*_ ''')
        numb = set("0123456789")
        rus = 0
        t = 0
        for k in text.lower():
            if k not in punc and k not in numb:
                if k in alph:
                    rus += 1
                    t += 1
                else:
                    t += 1
        if rus / t < 0.5:
            return None
        else:
            return text
    else:
        return None
    
def checkspaces(sentences):
    for i in range(len(sentences)):
        if len(sentences[i]) >= 2:
            if sentences[i][-2] == " ":
                sentences[i] = sentences[i][:-2] + sentences[i][-1]
        else:
            pass
    return sentences
    
def checkdoublespaces(sentences):
    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace("  ", " ").replace("   ", " ")
    return sentences

def checkemptysentences(sentences):
    newsent = []
    for s in sentences:
        if s == "" or s == " ":
            pass
        else:
            newsent.append(s)
    return newsent

def fresh_text(text):
    try:  
        
        #0 clean some shitty html symbols
        text = sub_html_text(text)
        
        #1 - make array of sentences
        sentences = make_sentences(text)
        
        #2 - in each sentence clean not words from start and end
        sentences = clean_tech(sentences)

        #3 - check that each next setnence it is not duplicate to previous ones
        sentences = clean_duplicates(sentences)

        #4 - add dots to end of sentences
        sentences = add_dots(sentences)
        
        #5 - decoding intefax
        sentences = interfaxdecode(sentences)
        
        #6 - cleaning some sh*t
        sentences = metalinkscleaner(sentences)
        
        #7 - "[...]"
        sentences = bayancleaner(sentences)
        
        #8 - cleaning intext links
        sentences = links(sentences)
        
        #9 - cheking spaces before dots and shit-looking double and triplespaces
        sentences = checkemptysentences(sentences)
        sentences = checkspaces(sentences)
        sentences = checkdoublespaces(sentences)
    
        #10 - generate fresh_text
        temptext = "".join(sentences[0:2])
        fresh_text = temptext + " " + ' '.join(sentences[2:])
        
        #11 - final check for bad symbols and other languages       
        fresh_text = russianlang(fresh_text).replace("  ", " ").replace("   ", " ")
        
    except:
        traceback.print_exc()
        fresh_text = text
        
    print(f'new text!: {fresh_text}')
    
    return fresh_text
