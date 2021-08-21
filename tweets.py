import get_news

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

twitter_config = configparser.ConfigParser()
twitter_config.read('config.ini')

access_token = twitter_config['twitterAuth']['access_token']
access_token_secret = twitter_config['twitterAuth']['access_token_secret']
consumer_key = twitter_config['twitterAuth']['consumer_key']
consumer_secret = twitter_config['twitterAuth']['consumer_secret']


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
        self.api = API(self.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        try:
            self.api.verify_credentials()
        except Exception as e:
            self.logger.error("Error during Tweepy authentication")
            raise e
        
        self.logger.info("Tweepy API Authenticated")
    
    def tweet_search(self, query):
        """Search for tweets within previous 7 days.
            Inputs: 
                https-encoded query
                language
                'until' date
                geocode (latitude/longitude)
            Returns: 
                Tweet object
        """
        self.tweet_search_list = []
        query = urllib.parse.urlencode(query)
        # latitude & longitude of Colombus, OH, USA
        latitude = '39.9828671'
        longitude = '-83.1309131'
        # radius of united states
        radius = '3881mi'

        query_result = tweepy.Cursor(self.api, q=query, lang='en', until={
                                     date.today()}, geocode=[latitude, longitude, radius])

        for status in tweepy.Cursor(query_result).items():
            self.tweet_search_list.append(status)
            return self.tweet_search_list

        # TODO append tweets to dataframe & return it
        self.tweet_search_df = pd.DataFrame(self.tweet_search_list)
        return self.tweet_search_df
        

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
                self.tweets_df['created_at'] = pd.to_datetime(self.tweets_df['created_at']) #TODO .apply method
                self.tweets_df.dropna(axis=0, how='any')

                return self.tweets_df
            
        if self.num_tweets < 450:  # whatever the max stream rate is for the twitter API Client
            return True
        else:
            return False



