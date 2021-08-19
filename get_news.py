from numpy import datetime64
from database import *
import logging
from datetime import date, datetime, timedelta
import pandas as pd
import json
import requests

# configure logger
logging.basicConfig(filename='news.log', filemode='w',
                    format=f'%(asctime)s - %(levelname)s - %(message)s')

# connect to db
connection = create_db_connection(host, username, password, db)

# execute defined queries to create db tables
execute_query(connection, create_article_table)
execute_query(connection, create_tweets_table)
execute_query(connection, create_political_event_table)
execute_query(connection, create_tiktok_sounds_table)
execute_query(connection, create_tiktok_music_table)

execute_query(connection, create_tiktok_stats_table)  # not running?
execute_query(connection, create_tiktok_tags_table)
execute_query(connection, create_tiktoks_table)

pop_news = []
top_headlines = []
best_words = []
word_df = {}


def request_pop_news():
    
    params = {
        'q': ['politics' or 'political' or 'law' or 'legal' or 'policy'],
        'from': {date.today() - timedelta(days=3)},
        'to': {date.today},
        'language': 'en',
        'sort_by': 'popularity'
    }

    headers = {
        'X-Api-Key': c['newsAuth']['api_key']
    }

    url = 'https://newsapi.org/v2/everything'

    # response as JSON dict
    response = requests.get(url, params=params, headers=headers).json()

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
            pop_news.append(pop_obj)

        return pop_news


def get_top_headlines():
    params = {
        "language": "en",
        "country": "us"
    }
    headers = {
        "X-Api-Key": c['newsAuth']['api_key']
    }
    url = "https://newsapi.org/v2/top-headlines"

    response = requests.get(
        url, params=params, headers=headers).json()  # response JSON dict

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
            top_headlines.append(story_obj)

        return top_headlines


# call function
request_pop_news()

# load function call results into Pandas dataframe
# flatten data to dataframe
pop_news = pd.json_normalize(pop_news, record_path=['articles'])
pop_news_df = pd.DataFrame(
    pop_news, columns=['title', 'author', 'url', 'publishedAt'])
pop_news_df = pop_news_df.dropna(axis=0, how='any')
pop_news_df.head()

# flatten data to dataframe
get_top_headlines()
top_headlines = pd.json_normalize(top_headlines, record_path=['articles'])
top_headlines_df = pd.DataFrame(
    top_headlines, columns=["title", "author", "url", "publishedAt"])
top_headlines_df = top_headlines_df.dropna(axis=0, how='any')

# top_headlines_df.head(20)

# put all news together
all_news = pd.concat([top_headlines_df, pop_news_df])

# convert to datetime
all_news['publishedAt'] = all_news['publishedAt'].apply(
    lambda row: datetime.strptime(row, '%Y-%m-%d %H:%M:%S'), #check formatting
    axis=0)

# execute mogrify
connection = create_db_connection( c['database']['host'], 
                                    c['database']['user'], 
                                    c['database']['password'], 
                                    c['database']['database'])
execute_mogrify(connection, all_news, 'articles')


