""""Extract keywords from  news articles to use as search values for TikTok & Twitter posts relating to the political event of interest. """

from numpy import datetime64
from database import *
import logging
from datetime import date, datetime, timedelta
import pandas as pd
import json
import requests
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from operator import itemgetter
import math
from bs4 import BeautifulSoup
# from django.db import DatabaseError

# best_words = []
# word_df = {}

class News():
    def __init__(self, api_key, logger=logging):
        self.api_key = api_key
        self.logger = logging.basicConfig(filename='news.log', filemode='w',
                    format=f'%(asctime)s - %(levelname)s - %(message)s')

    @Timer("Popular News")
    def request_pop_news(self, params={
        'q': ['politics' or 'political' or 'law' or 'legal' or 'policy'],
        'from': {date.today() - timedelta(days=3)},
        'to': {date.today},
        'language': 'en',
        'sort_by': 'popularity'
    }):
        self.pop_news = []
        self.params = params

        headers = {
            'X-Api-Key': self.api_key
        }

        url = 'https://newsapi.org/v2/everything'

        # response as JSON dict
        response = requests.get(url, params=self.params, headers=headers).json()

        with open('pop_news.json', 'w') as f:
            # write results to JSON file
            json.dump(response, f)

        with open('pop_news.json', 'r') as file:
            # create Python list object from JSON
            pop_news_json = file.read().split("\n")

            for story in pop_news_json:
                pop_obj = json.loads(story)

                if 'title' in pop_obj:
                    pop_obj['title'] = pop_obj['articles']['title']
                if 'author' in pop_obj:
                    pop_obj['author'] = pop_obj['articles']['author']
                if 'url' in pop_obj:
                    pop_obj['url'] = pop_obj['articles']['url']
                if 'publishedAt' in pop_obj:
                    pop_obj['publishedAt'] = pop_obj['articles']['publishedAt']

                # add info to pop_news dict
                self.pop_news.append(pop_obj)
        
        # load returned results into Pandas dataframe
        # flatten data to dataframe
        pop_news = pd.json_normalize(self.pop_news, record_path=['articles'])
        self.pop_news_df = pd.DataFrame(
                pop_news, columns=['title', 'author', 'url', 'publishedAt'])
        self.pop_news_df.dropna(axis=0, how='any')

        return self.pop_news_df

    @Timer("Top Headlines")
    def get_top_headlines(self, params={
        "language": "en",
        "country": "us"
    }):

        self.top_headlines = []
        self.params = params

        headers = {
            "X-Api-Key": self.api_key
        }
        url = "https://newsapi.org/v2/top-headlines"

        response = requests.get(
            url, params=self.params, headers=headers).json()  # response JSON dict

        with open("top_headlines.json", "w") as f:
            # write results to JSON file
            json.dump(response, f)

        with open("top_headlines.json", "r") as file:
            # create Python object from JSON
            top_headlines_json = file.read().split("\n")

            for story in top_headlines_json:
                story_obj = json.loads(story)

                if 'title' in story_obj:
                    story_obj["title"] = story_obj["articles"]["title"]
                if 'author' in story_obj:
                    story_obj["author"] = story_obj["articles"]["author"]
                if 'url' in story_obj:
                    story_obj["url"] = story_obj["articles"]["url"]
                if 'publishedAt' in story_obj:
                    story_obj["publishedAt"] = story_obj["articles"]["publishedAt"]

                # add info to top_headlines list/dict
                self.top_headlines.append(story_obj)
            
        # flatten data to dataframe
        top_headlines = pd.json_normalize(self.top_headlines, record_path=['articles'])
        self.top_headlines_df = pd.DataFrame(
                top_headlines, columns=["title", "author", "url", "publishedAt"])
        self.top_headlines_df.dropna(axis=0, how='any')

        return self.top_headlines_df

    # put all news together
    def all_news(self):
        # call class functions
        top_headlines = self.get_top_headlines()
        pop_news = self.request_pop_news()

        # combine result dfs
        self.all_news_df = pd.concat([top_headlines, pop_news])

        # convert to datetime
        self.all_news_df['publishedAt'] = self.all_news_df['publishedAt'].apply(
            lambda row: datetime.strptime(row, '%Y-%m-%d %H:%M:%S'), # TODO check formatting
            axis=0)

        return self.all_news_df

    
    def article_text(self, url):
        """Get news article text using Requests and BeautifulSoup"""
        #create dataframe to store text
        self.article_text_df = pd.DataFrame({'index': '',
                                'title': '',
                                'text': '',
                                'keyword1': '',
                                'keyword2': '',
                                'keyword3': ''
                                })

        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html)
        text = soup.get_text()

        return text

    def keyword_extraction(self, text):
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
        self.tf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words:
                if each_word in self.tf_score:
                    self.tf_score[each_word] += 1
                else:
                    self.tf_score[each_word] = 1

        # Divide by total_word_length for each dictionary element
        self.tf_score.update((x, y/int(total_word_length))
                        for x, y in self.tf_score.items())  # test - ZeroError

        #calculate IDF for each word
        self.idf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words:
                if each_word in self.idf_score:
                    self.idf_score[each_word] = self.check_sent(each_word, total_sentences)
                else:
                    self.idf_score[each_word] = 1

        # Performing a log and divide
        self.idf_score.update((x, math.log(int(total_sent_len)/y))
                        for x, y in self.idf_score.items())

        # Calculate IDF * TF for each word
        self.tf_idf_score = {key: self.tf_score[key] *
                        self.idf_score.get(key, 0) for key in self.tf_score.keys()}

        return self.tf_idf_score

    def check_sent(self, word, sentences):
        """Check if word is present in sentence list for calculating IDF (Inverse Document Frequency)"""
        final = [all([w in x for w in word]) for x in sentences]
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    
        return int(len(sent_len))

    def get_top_n(self, dict_elem, n):
        """Calculate most important keywords in text of interest"""
        result = dict(sorted(dict_elem.items(),
                    key=itemgetter(1), reverse=True)[:n])
        return result
