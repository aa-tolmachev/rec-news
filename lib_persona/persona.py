import markovify
import os

from lib_log import simple_log
global module_name
module_name = os.path.basename(__file__) #module name file

with open ("./data/telegram_zhabi.txt", "r") as myfile:
    persona_context =myfile.readlines()
persona_context = " ".join(persona_context)


def add_persona_first_sentence(text):
    global module_name
    step = 0

    global persona_model


    #make markov models of persona and text
    persona_model = markovify.Text(persona_context)
    text_model = markovify.Text(text)
    step = simple_log.make_log('i',module_name , step, message=f'create markov models' )
    
    #make combo markov model
    model_combo = markovify.combine([ persona_model, text_model ], [ 2, 10 ])
    
    #generate sentences
    names = ['Сан', 'Макс','Гриш','stqr','Грих','Коля','Бельгии','\\u','?','0','собеседовании' ,'Александр'
            ,'Видос', 'Толмач','https']

    max_persona_sentence = ''
    max_persona_sentence_len = 0

    for i in range(30):
        p_sentence = model_combo.make_sentence()
        if p_sentence:
            #check names
            is_name = 0
            for n in names:
                if n in p_sentence:
                    is_name = 1
            if is_name == 0 and len(p_sentence) > max_persona_sentence_len:
                max_persona_sentence = p_sentence
                max_persona_sentence_len = len(p_sentence)
    step = simple_log.make_log('i',module_name , step, message=f'make persona fst sentence - {max_persona_sentence}' )


            
    #make text with persona first sentence
    if max_persona_sentence != '':
        text = max_persona_sentence, '\n\n',text

    step = simple_log.make_log('end',module_name , step, message=f'first persona sentence added' )
        
    return text
    

