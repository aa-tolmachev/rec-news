import nltk
from nltk.tokenize import sent_tokenize

def format_message(text):
    sentences = sent_tokenize(text, language='russian')
    sentences[0] = "<b>" + sentences[0] + "</b>\n"
    result = " ".join(sentences)
    return result

def format_comment(comment):
    if comment[0] in [' ', '\n']:
        comment = comment[1:]
    first_letter = comment[0].upper()
    comment = first_letter + comment[1:]
    return comment

