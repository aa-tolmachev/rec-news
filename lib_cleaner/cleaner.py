import re
import numpy as np
import collections

from numpy import dot
from numpy.linalg import norm
import traceback

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
        
def fresh_text(text):
    try:
        #1 - make array of sentences
        sentences = make_sentences(text)

        #2 - in each sentence clean not words from start and end
        sentences = clean_tech(sentences)

        #3 - check that each next setnence it is not duplicate to previous ones
        sentences = clean_duplicates(sentences)

        #4 - add dots to end of sentences
        sentences = add_dots(sentences)

        #5 - final generate fresh_text
        fresh_text = ' '.join(sentences)
    except:
        traceback.print_exc()
        fresh_text = text
        
    print(f'new text!: {fresh_text}')
    
    return fresh_text