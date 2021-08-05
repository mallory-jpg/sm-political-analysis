# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # NewsAPI.org-4 Data Collection
# - Goal: Find top news by day
# - Incrementally-updated political news will be compared against twitter and tiktok activity to asses responses to political events in the United States.
# 
# ## Version 4: Counts words in title, not in body text of article + changed db connection info

# %%
# Import necessary modules
import pandas as pd
from pandas.io import sql
import json
import requests
from datetime import date, timedelta
# from bs4 import BeautifulSoup
import numpy as np
from sqlalchemy import create_engine
import logging
import psycopg2
from psycopg2 import Error
import configparser


# %%
c = configparser.ConfigParser()
c.read('sm_config.ini')

# config credentials
host = c['PostgreSQLdb']['host']
username = c['PostgreSQLdb']['user']
password = c['PostgreSQLdb']['password']
db = c['PostgreSQLdb']['database']


# %%
# configure logger
logging.basicConfig(filename='news.log', filemode='w',
                    format=f'%(asctime)s - %(levelname)s - %(message)s')


# %%
def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = psycopg2.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        logging.info("PostgreSQL Database connection successful")
    except Error as err:
        logging.error(f"Error: '{err}'")

    return connection


# %%
def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        logging.info("Database created successfully")
    except Error as err:
        logging.error(f"Error: '{err}'")


# %%
def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = psycopg2.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )
        # cursor = connection.cursor()
        logging.info("PostgreSQL Database connection successful")
    except Error as err:
        logging.error(f"Error: '{err}'")

    return connection


# %%
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        logging.info("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


# %%
# connect to server
server = create_server_connection(host, username, password)

# create sm_news database
create_database_query = """
    CREATE DATABASE IF NOT EXISTS sm_news; 
"""
# create_database(server, create_database_query)


# %%

# create necessary tables
create_article_table = """
CREATE TABLE IF NOT EXISTS articles (
    publishedAt DATE,
    title VARCHAR PRIMARY KEY,
    author VARCHAR,
    url TEXT, 
    keyWords VARCHAR
    );
"""
# CREATE INDEX index ON articles(publishedAt);
create_political_event_table = """
CREATE TABLE IF NOT EXISTS event (
    eventID VARCHAR PRIMARY KEY,
    startDate DATE,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    keyWords VARCHAR
    );
"""
create_tweets_table = """
CREATE TABLE IF NOT EXISTS tweets (
    tweet_id INT PRIMARY KEY,
    publishedAt DATE NOT NULL,
    userID INT NOT NULL,
    tweet VARCHAR NOT NULL,
    location VARCHAR NOT NULL, 
    tags VARCHAR NOT NULL
    );
"""
create_tiktoks_table = """
CREATE TABLE IF NOT EXISTS tiktoks (
    postID INT PRIMARY KEY,
    createTime DATE NOT NULL,
    description VARCHAR NOT NULL,
    musicID VARCHAR NOT NULL,
    tags VARCHAR NOT NULL,
    FOREIGN KEY(songID) REFERENCES tiktok_music(songID),
    FOREIGN KEY(soundID) REFERENCES tiktok_sounds(soundID),
    FOREIGN KEY(userID) REFERENCES users(userID)
    );
"""
create_tiktok_sounds_table = """
CREATE TABLE IF NOT EXISTS tiktok_sounds (
    soundID INT PRIMARY KEY,
    soundTitle VARCHAR,
    isOriginal BOOLEAN
    );
"""
create_tiktok_music_table = """
CREATE TABLE IF NOT EXISTS tiktok_music (
    songID INT PRIMARY KEY,
    songTitle VARCHAR NOT NULL
    );
"""
create_tiktok_stats_table = """
CREATE TABLE IF NOT EXISTS tiktok_stats (
    FOREIGN KEY(postID) REFERENCES tiktoks(postID),
    shareCount INT,
    commentCount INT,
    playCount INT,
    diggCount INT
    );
"""

create_tiktok_tags_table = """
CREATE TABLE IF NOT EXISTS tiktok_tags (
    tagID INT PRIMARY KEY,
    tag_name VARCHAR NOT NULL 
    );
"""
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    userID INT PRIMARY KEY,
    username VARCHAR NOT NULL,
    user_bio VARCHAR NOT NULL
    );
"""
delete_bad_data = """
DELETE FROM articles
    WHERE publishedAt IS NULL;
"""


# %%

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


# %%
# read query
def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


# %%
pop_news = []


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


# call function
request_pop_news()

# load function call results into Pandas dataframe

# flatten data to dataframe
pop_news = pd.json_normalize(pop_news, record_path=['articles'])
pop_news_df = pd.DataFrame(
    pop_news, columns=['title', 'author', 'url', 'publishedAt'])
pop_news_df = pop_news_df.dropna(axis=0, how='any')
pop_news_df.head()


# %%
# get top headlines
top_headlines = []


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


# flatten data to dataframe
get_top_headlines()
top_headlines = pd.json_normalize(top_headlines, record_path=['articles'])
top_headlines_df = pd.DataFrame(
    top_headlines, columns=["title", "author", "url", "publishedAt"])
top_headlines_df = top_headlines_df.dropna(axis=0, how='any')

top_headlines_df.head(20)


# %%
all_news = pd.concat([top_headlines_df, pop_news_df])
all_news['publishedAt'] = pd.to_datetime(all_news['publishedAt'])

all_news.info()
all_news.head()


# %%
def execute_mogrify(conn, df, table):
    """
    Using cursor.mogrify() to build the bulk insert query
    then cursor.execute() to execute the query
    """
    # Create a list of tupples from the dataframe values
    tuples = [tuple(x) for x in df.to_numpy()]
    # Comma-separated dataframe columns
    cols = ','.join(list(df.columns))
    # SQL query to execute
    cursor = conn.cursor()
    values = [cursor.mogrify("(%s,%s,%s,%s)", tup).decode('utf8')
              for tup in tuples]
    # if not publishedAt, delete record
    query = "INSERT INTO %s(%s) VALUES" % (table, cols) + ",".join(values)

    try:
        cursor.execute(query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("Error: %s" % error)
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        conn.close()
        return 1
    logging.info("execute_mogrify() done")
    cursor.close()
    conn.close()


# %%
connection = create_db_connection("localhost", "postgres", "521368", "sm_news")
execute_mogrify(connection, all_news, 'articles')


