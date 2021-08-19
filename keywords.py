""""Extract keywords from NewsAPI.org news articles to use as search values for TikTok & Twitter posts relating to the political event of interest. """

from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from operator import itemgetter
import math


def keyword_extraction(text):
    """Determine weight of important words in articles and add to articles_text table
        using TF-IDF ranking"""

    # make sure text is in string format for parsing
    text = str(text)
    stop_words = set(stopwords.words('english'))
    
    # find total words in document for calculating Term Frequency (TF)
    total_words = text.split()
    total_word_length = len(total_words)
    
    # find total number of sentences for calculating Inverse Document Frequency
    total_sentences = tokenize.sent_tokenize(text)
    total_sent_len = len(total_sentences)
    
    # calculate TF for each word
    tf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.', '')
        if each_word not in stop_words:
            if each_word in tf_score:
                tf_score[each_word] += 1
            else:
                tf_score[each_word] = 1

    # Divide by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_word_length))
                    for x, y in tf_score.items())  # test - ZeroError

    #calculate IDF for each word
    idf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.', '')
        if each_word not in stop_words:
            if each_word in idf_score:
                idf_score[each_word] = check_sent(each_word, total_sentences)
            else:
                idf_score[each_word] = 1

    # Performing a log and divide
    idf_score.update((x, math.log(int(total_sent_len)/y))
                     for x, y in idf_score.items())

    # Calculate IDF * TF for each word
    tf_idf_score = {key: tf_score[key] *
                    idf_score.get(key, 0) for key in tf_score.keys()}

    # get top 3 words of significance
    print(get_top_n(tf_idf_score, 3))


def check_sent(word, sentences):
    """Check if word is present in sentence list for calculating IDF (Inverse Document Frequency)"""
    final = [all([w in x for w in word]) for x in sentences]
    sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    return int(len(sent_len))

def get_top_n(dict_elem, n):
    result = dict(sorted(dict_elem.items(),
                  key=itemgetter(1), reverse=True)[:n])
    return result



