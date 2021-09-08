# import dependencies
import pandas as pd
import json
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
import numpy as np
import logging
import configparser
from timer import Timer
from numpy import datetime64
from datetime import date, datetime, timedelta
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from operator import itemgetter
import math
import tweepy  # python package for accessing Tweet streaming API
from tweepy import API
from tweepy import Stream
import urllib.parse
import psycopg2  # alts: SQLalchemy
from TikTokAPI import TikTokAPI
from selenium import webdriver
from psycopg2 import Error
import re
import sys
import geocoder
from kafka import KafkaProducer
from helper_functions import *
import time

# import program modules
from database import *
from tiktok import *
from tweets import *
from news import *



c = configparser.ConfigParser()
c.read('config.ini')

# config credentials
host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['database']

news_api_key = c['newsAuth']['api_key']
tiktok_sv_id = c['tiktokAuth']['s_v_web_id']
tiktok_tt_id = c['tiktokAuth']['tt_webid']

# twitter auth
access_token = c['twitterAuth']['access_token']
access_token_secret = c['twitterAuth']['access_token_secret']
consumer_key = c['twitterAuth']['consumer_key']
consumer_secret = c['twitterAuth']['consumer_secret']


postgres_db = DataBase(host, username, password)
# connect to server
postgres_server = postgres_db.create_server_connection()
# connect to social media news db
connection = postgres_db.create_db_connection(db)

# execute defined queries to create db tables if needed
try:
    postgres_db.execute_query(connection, create_article_table)
    postgres_db.execute_query(connection, create_article_text_table)
    postgres_db.execute_query(connection, create_tweets_table)
    postgres_db.execute_query(connection, create_political_event_table)
    postgres_db.execute_query(connection, create_users_table)
    postgres_db.execute_query(connection, create_tiktok_sounds_table)
    postgres_db.execute_query(connection, create_tiktok_music_table)
    postgres_db.execute_query(connection, create_tiktok_stats_table)
    postgres_db.execute_query(connection, create_tiktok_tags_table)
    postgres_db.execute_query(connection, create_tiktoks_table)
except (ConnectionError) as e:
    logging.error({e}, 'Check SQL create queries')

# add foreign keys
try:
    postgres_db.execute_query(connection, alter_tiktoks_table)
    postgres_db.execute_query(connection, alter_tiktok_stats_table)
except (ConnectionError) as e:
    logging.error({e}, 'Check SQL alteration queries')

# instantiate News class
news = News(news_api_key)
# get all news & keywords - takes about 30 seconds
news.get_all_news()
keywords = news.get_all_news()
tw = t.tweet_search(keywords)

# instantiate Tweets class
t = Tweets(consumer_key, consumer_secret, access_token, access_token_secret)
# authenticate Tweepy
auth = t.tweepy_auth()


tiktok_auth = {
    "s_v_web_id": tiktok_sv_id,  # references variables saved from config file
    "tt_webid": tiktok_tt_id
}
api = TikTokAPI(cookie=tiktok_auth)
tiktok_df = news.all_news_df['keywords'].map(api.getVideosByHashtag)

# add late-arriving twitter data
# tweet stream
stream = tweetStream(consumer_key, consumer_secret,
                     access_token, access_token_secret)
stream.periodic_batch(20) # get periodic updates

# mogrify stream
postgres_db.execute_mogrify(connection, stream, 'stream_tweets')
# mogrify batch tweets
postgres_db.execute_mogrify(connection, tw, 'batch_tweets')
# execute mogrify - insert news df into database
postgres_db.execute_mogrify(connection, news.all_news_df, 'articles')
# mogrify
postgres_db.execute_mogrify(connection, tiktok_df, 'tiktoks')

