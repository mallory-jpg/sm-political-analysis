"""Compute weight of words in articles and titles"""

# from django.db import DatabaseError
# from get_news import *
import requests
from bs4 import BeautifulSoup
# from database import *
import logging
import re
from nltk import sent_tokenize, tokenize
from nltk.corpus import stopwords
import nltk
from datetime import datetime, date, timedelta
import json
import pandas as pd
import math
from operator import itemgetter
import numpy as np
# from keywords import *
import configparser
from helper_functions import get_random_ua

# TODO to get events -> group by itertools combinations of keywords - if it has a combination of all three keywords then group together

c = configparser.ConfigParser()
c.read('config.ini')

news_api_key = c['newsAuth']['api_key']

class News():
    """Extract keywords from  news articles to use as search values for TikTok & Twitter posts relating to the political event of interest. """

    def __init__(self, api_key, logger=logging):
        self.api_key = api_key
        self.logger = logging.basicConfig(filename='news.log', filemode='w',
                                          format=f'%(asctime)s - %(levelname)s - %(message)s')

    def request_pop_news(self, params={
        'q': ['politics' or 'political' or 'law' or 'legal' or 'policy'],
        'from': {date.today() - timedelta(days=3)},
        'to': {date.today},
        'language': 'en',
        'sort_by': 'popularity'
    }):
        pop_news = []
        self.params = params

        headers = {
            'X-Api-Key': self.api_key,
            # get_random_ua for Chrome
            'user-agent': get_random_ua('Chrome')
        }

        url = 'https://newsapi.org/v2/everything'

        try:
            # response as JSON dict
            self.response = requests.get(
                url, params=self.params, headers=headers).json()
        except requests.ConnectionError as err:
            logging.error(err)
            raise err
        else:
            logging.info('Popular news request successful')

        with open('pop_news.json', 'w') as f:
            # write results to JSON file
            json.dump(self.response, f)

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
                pop_news.append(pop_obj)

        return pop_news

    def get_top_headlines(self, params={
        "language": "en",
        "country": "us"
    }):

        top_headlines = []
        self.params = params

        headers = {
            "X-Api-Key": news_api_key,
            "user-agent": get_random_ua('Chrome')
        }
        url = "https://newsapi.org/v2/top-headlines"
        try:
            self.response = requests.get(
                url, params=self.params, headers=headers).json()  # response JSON dict
        except requests.ConnectionError as err:
            logging.error(err)
            raise err
        else:
            logging.info('Top headlines request successful')

        with open("top_headlines.json", "w") as f:
            # write results to JSON file
            json.dump(self.response, f)

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
                top_headlines.append(story_obj)

        return top_headlines

    # put all news together
    def get_all_news(self):
        """Combines top headlines and popular news into one Pandas DataFrame."""
        try:
            top_headlines = self.get_top_headlines()
            pop_news = self.request_pop_news()
        except requests.Timeout as err:
            logging.error(err, '')
            raise err
        except KeyboardInterrupt as i:
            logging.critical(i, 'News request interrupted - taking too long')
        else:
            logging.info('News request successful')
            # noramlize nested JSON
            pop_news = pd.json_normalize(pop_news, record_path=['articles'])
            top_headlines = pd.json_normalize(
                top_headlines, record_path=['articles'])
            all_news = top_headlines.append(pop_news)

            # create dataframe from combined news list
            self.all_news_df = pd.DataFrame(
                all_news, columns=['title', 'author', 'url', 'publishedAt', "text"])
            self.all_news_df.drop_duplicates()

        # convert to datetime
        self.all_news_df['publishedAt'] = self.all_news_df['publishedAt'].map(
            lambda row: datetime.strptime(str(row), "%Y-%m-%dT%H:%M:%SZ") if pd.notnull(row) else row)
        # set index to publishing time, inplace to apply to same df instead of copy or view
        self.all_news_df.set_index('publishedAt', inplace=True)

        # apply .get_article_text() to text column of df
        self.all_news_df["text"] = self.all_news_df["url"].apply(
            self.get_article_text)
        # get keywords from article text
        self.all_news_df["keywords"] = self.all_news_df['text'].apply(
            self.keyword_extraction)
        # get top n=3 words of significance
        self.all_news_df["keywords"] = self.all_news_df["keywords"].apply(
            self.get_top_n, n=3)

        return self.all_news_df

    def get_article_text(self, url):
        """Clean & process news article text to prepare for keyword extraction"""

        contractions_dict = {"'s": " is", "n't": " not", "'m": " am", "'ll": " will",
                             "'d": " would", "'ve": " have", "'re": " are"}
        symbols_list = ['&', '+', '-', '/', '|', '$', '%', ':', '(', ')', '?']

        # request
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, features="lxml")
        a_text = soup.get_text()

        # remove newline characters
        a_text = a_text.strip()
        # split joined words
        a_text = " ".join([s for s in re.split(
            "([A-Z][a-z]+[^A-Z]*)", a_text) if s])
        # remove mentions
        a_text = re.sub("@\S+", " ", a_text)
        # remove URLs
        a_text = re.sub("https*\S+", " ", a_text)
        # remove hashtags
        a_text = re.sub("#\S+", " ", a_text)
        # remove unicode characters
        a_text = a_text.encode('ascii', 'ignore').decode()
        # replace contractions
        for key, value in contractions_dict.items():
            if key in a_text:
                a_text = a_text.replace(key, value)
        # remove symbols and punctuation
        for i in symbols_list:
            if i in a_text:
                a_text = a_text.replace(i, '')

        # make lowercase
        a_text = a_text.lower()
        a_text = re.sub(r'\w*\d+\w*', '', a_text)

        return a_text

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
        tf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words and len(each_word) > 3:
                if each_word in tf_score:
                    tf_score[each_word] += 1
                else:
                    tf_score[each_word] = 1

        # Divide by total_word_length for each dictionary element
        tf_score.update((x, y/int(total_word_length))
                        for x, y in tf_score.items())  # TODO test - ZeroError

        #calculate IDF for each word
        idf_score = {}
        for each_word in total_words:
            each_word = each_word.replace('.', '')
            if each_word not in stop_words and len(each_word) > 3:
                if each_word in idf_score:
                    idf_score[each_word] = self.check_sent(
                        each_word, total_sentences)
                else:
                    idf_score[each_word] = 1

        # Performing a log and divide
        idf_score.update((x, math.log(int(total_sent_len)/y))
                         for x, y in idf_score.items())

        # Calculate IDF * TF for each word
        tf_idf_score = {key: tf_score[key] *
                        idf_score.get(key, 0) for key in tf_score.keys()}

        return tf_idf_score

    def check_sent(self, word, sentences):
        """Check if word is present in sentence list for calculating IDF (Inverse Document Frequency)"""
        final = [all([w in x for w in word]) for x in sentences]
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]

        return int(len(sent_len))

    def get_top_n(self, dict_elem, n):
        """Calculate most important keywords in text of interest"""
        result = dict(sorted(dict_elem.items(),
                             key=itemgetter(1), reverse=True)[:n])
        result = result.keys()

        return result
