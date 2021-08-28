from news import *

import tweepy  # python package for accessing Tweet streaming API
from tweepy import API
from tweepy import Stream
import json
import logging
import pandas as pd
import configparser
import requests
from datetime import date, timedelta
import urllib.parse

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
        #self.logger = logging.basicConfig(filename='tweets.log', filemode='w',
                                         #format=f'%(asctime)s - %(levelname)s - %(message)s')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.logger = logging.getLogger(__name__)

    def tweepy_auth(self):

        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)

        # create API object
        self.api = API(self.auth, wait_on_rate_limit=True) #wait_on_rate_limit_notify=True)

        try:
            self.api.verify_credentials()
        except Exception as e:
            self.logger.error("Error during Tweepy authentication")
            raise e
        
        self.logger.info("Tweepy API Authenticated")
    
    def tweet_search(self, keyword_dict):
        """Search for tweets within previous 7 days.
            Inputs: 
                keyword list
            Returns: 
                Tweet list
        """
        self.tweet_search_dict = {}
        # collect tweets, filter out retweets
        for word in keyword_dict.keys():
            tweets = tweepy.Cursor(self.api.search_tweets, q=str(word) + " -filter:retweets", lang='en').items()
            self.tweet_search_dict = {
                [tweet.id, tweet.user.id, tweet.user.location, tweet.created_at, tweet.text] for tweet in tweets}

        self.tweet_search_df = pd.DataFrame.from_dict(self.tweet_search_dict, columns=[
                                            "tweet_id", "user_id", "location", "createdAt", "tweet_text"])
        self.tweet_search_df.set_index("tweet_id")
        return self.tweet_search_df
        
    def tweet_trends(self):
            # returns JSON
        # 1 refers to USA WOEID 
        self.tweet_trends_list = []
        result = tweepy.Cursor(self.api.trends_place(1))

        for trend in tweepy.Cursor(result).items():
            self.tweet_trends_list.append(trend)
            return self.tweet_trends_list
        
        #TODO append to dataframe
        self.tweet_trends_df = pd.DataFrame(self.tweet_trends_list)
        return self.tweet_trends_df    

# define stream listener class
class TwitterStreamListener(tweepy.StreamListener):
    def __init__(self, api=None):
        super(TwitterStreamListener, self).__init__()
        self.num_tweets = 0
        # self.file = open('tweets.txt', 'w')
        # self.db = ''
        self.tweet_list = []
        # self.file = open("tweets.json", "w")

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


keywords = dict(news.all_news_df["keywords"])

#print(keywords)
t = Tweets(consumer_key, consumer_secret, access_token, access_token_secret)
auth = t.tweepy_auth()
# search_df = t.tweet_search(keywords)

print(t.tweet_search_df)
