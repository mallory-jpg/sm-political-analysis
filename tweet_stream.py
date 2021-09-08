import tweepy
from kafka import KafkaProducer
import json
import time
import configparser

c = configparser.ConfigParser()
c.read('config.ini')

# authenticate twitter credentials
access_token = c['twitterAuth']['access_token']
access_token_secret = c['twitterAuth']['access_token_secret']
consumer_key = c['twitterAuth']['consumer_key']
consumer_secret = c['twitterAuth']['consumer_secret']

# authenticate tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# set access token & secret
auth.set_access_token(access_token, access_token_secret)

# create API object
api = tweepy.API(auth)

# configue kafka
producer = KafkaProducer(bootstrap_servers='localhost')
topic_name = 'tweet-stream'
important_fields = ['created_at', 'id', 'id_str', 'text',
                    'retweet_count', 'favorite_count', 'favorited', 'retweeted', 'lang']

def get_twitter_data():
    result = 