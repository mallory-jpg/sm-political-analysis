from news import *

import tweepy  # python package for accessing Tweet streaming API
from tweepy import API
from tweepy import Stream
import json
import logging
import pandas as pd
import configparser
import requests
import geocoder
from datetime import date, timedelta
import sys
import psycopg2
# import urllib.parse

config = configparser.ConfigParser()
config.read('config.ini')

access_token = config['twitterAuth']['access_token']
access_token_secret = config['twitterAuth']['access_token_secret']
consumer_key = config['twitterAuth']['consumer_key']
consumer_secret = config['twitterAuth']['consumer_secret']

news_api_key = config['newsAuth']['api_key']

# instantiate News class
news = News(news_api_key)
# get all news - takes about 30 seconds
news.get_all_news()

class Tweets():
    
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret, logger=logging):
        self.logger = logging.basicConfig(filename='tweets.log', filemode='w',
                                          format=f'%(asctime)s - %(levelname)s - %(message)s')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.location = sys.argv[1]  # user location as argument variable
        # object with latitude & longitude of user location
        self.geo = geocoder.osm(self.location)

    def tweepy_auth(self):
        """Authorize tweepy API"""

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)

        # create API object
        self.api = API(self.auth, wait_on_rate_limit=True, user_agent=get_random_ua('Chrome'))# wait_on_rate_limit_notify=True)

        try:
            self.api.verify_credentials()
            logging.info("Tweepy API Authenticated")
            print('Tweepy authentication successful')
        except Exception as e:
            logging.error(f"Error during Tweepy authentication: {e}")
            raise e
        return self.api
    
    def get_tweets(self, news_keywords, news_instance): # TODO add stream listening stuff to params
        searched_tweets = self.tweet_search(news_keywords)
        # stream_tweets = TwitterStreamListener.on_status(listener, tweet_stream)

    def tweet_search(self, news_keywords):
        """Search for tweets within previous 7 days.
                    Inputs:
                        keyword list
                    Returns:
                        Tweet list => JSON
        """
        api = self.api

        # unpack keyword tuples
        print('Searching for tweets matching keywords')
        for keys in news_keywords:
            keywords = list(keys)  # TODO add itertools combinations
            for word in keywords:
                try:
                    result = api.search_tweets(q=str(
                                    word) + " -filter:retweets", lang='en')
                                # print(type(result))
                    status = result[0]
                                # print(type(status))
                    tweet = status._json
                    search_tweet_count = len(tweet)
                                #self.file.write(json.dumps(tweets)+ '\\n')
                    tweet = json.dumps(tweet)  # tweet to json string
                    assert (type(tweet) == str), "Tweet must be converted to JSON string"
                    tweet = json.loads(tweet)  # tweet to dict
                    assert (type(tweet) == dict), "Tweet must be converted from JSON string to type dict"
                except (TypeError) as e:
                    logging('Error: ', e)
                    print('Error: keyword not found in tweet search')
                    break
                else:
                    # write tweets to json file
                    with open("tweets.json", "a") as f:
                        json.dump(tweet, f)
        logging.info('Tweet search successful')
        print('Tweet search by keyword was successful')

        #finally:
        # TODO add tweet unpacking & cleaning?
        #pass
        # TODO put tweets into db
        # TODO

# Insert Tweet data into database


    def dbConnect(self, user_id, user_name, tweet_id, tweet, retweet_count, hashtags):
        """Insert tweets directly into database without intermediary dataframe
        https://www.analyticsvidhya.com/blog/2020/08/analysing-streaming-tweets-with-python-and-postgresql/#h2_6"""
        self.from_file = "sm-political-analysis/tweets.json" # get from this file and mogrify babyyyy

        conn = psycopg2.connect(host="localhost", database="TwitterDB", port=5432, user= '', password= '') # TODO fill in credentials

        cur = conn.cursor()

        # insert user information 
        # TODO change db info
        command = '''INSERT INTO TwitterUser (user_id, user_name) VALUES (%s,%s) ON CONFLICT
                    (User_Id) DO NOTHING;'''
        cur.execute(command, (user_id, user_name))

        # insert tweet information
        command = '''INSERT INTO TwitterTweet (tweet_id, user_id, tweet, retweet_count) VALUES (%s,%s,%s,%s);'''
        cur.execute(command, (tweet_id, user_id, tweet, retweet_count))

        # insert entity information
        for i in range(len(hashtags)):
            hashtag = hashtags[i]
            command = '''INSERT INTO TwitterEntity (tweet_id, hashtag) VALUES (%s,%s);'''
            cur.execute(command, (tweet_id, hashtag))

        # Commit changes
        conn.commit()

        # Disconnect
        cur.close()
        conn.close()
    def clean_tweets(self, tweets):
        # use slang.txt
        # https://www.geeksforgeeks.org/python-efficient-text-data-cleaning/
        pass

# define stream listener class
class TwitterStreamListener(tweepy.Stream):
    def __init__(self, api=None):
        super(tweepy.Stream, self).__init__()
        # super(json.JSONEncoder, self).__init__()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.api = api

        self.num_tweets = 0
        # self.file = open('tweets.txt', 'w')
        self.tweet_list = []

    # def toJson(self):
    #     return json.dumps(self, default=lambda o: o.__dict__)
    
    def on_status(self, status):
        tweet = status._json

        with open("tweets.json", "w") as f:
            # write tweets to json file
            json.dump(tweet, f)
        
        with open("tweets.json", "r") as file:
            # create python object from json
            tweets_json = file.read().split("\n")

            for tweet in tweets_json:
                tweet_obj = json.loads(tweet)

                #flatten nested fields
                if 'quoted_status' in tweet_obj:
                    tweet_obj['quote_tweet'] =tweet_obj['quoted_status']['extended_tweet']['full_text']
                if 'user' in tweet_obj:
                    tweet_obj['location'] = tweet_obj['user']['location']
                # if 'created_at' in tweet_obj:
                #     tweet_obj['created_at'] = pd.to_datetime(tweet)
                

                self.tweet_list.append(status)
                self.num_tweets += 1

                # flatten data to dataframe
                # tweets = pd.json_normalize(self.tweet_list, record_path=['articles'])
                self.tweets_df = pd.DataFrame(self.tweet_list, columns=["tweet_id", "publishedAt", "userID", "text", "location"])

                return self.tweets_df
            
        if self.num_tweets < 450:  # whatever the max stream rate is for the twitter API Client
            return True
        else:
            return False


# keywords = dict(news.all_news_df["keywords"])

#print(keywords)
t = Tweets(consumer_key, consumer_secret, access_token, access_token_secret)
auth = t.tweepy_auth()
# search_df = t.tweet_search(keywords)


