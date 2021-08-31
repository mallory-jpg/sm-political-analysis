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
import geocoder
import sys

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

def tweet_cleaner():
    """Clean tweets from stream and search"""
    pass

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
            print('Tweepy Authentication successful')
        except Exception as e:
            logging.error(f"Error during Tweepy authentication: {e}")
            raise e
        return self.api
    
    def get_tweets(self, news_keywords, news_instance): # TODO add stream listening stuff to params
        searched_tweets = self.tweet_search(news_keywords)
        stream_tweets = TwitterStreamListener.on_status(listener, tweet_stream)

        # all_tweets = {}
        # # process tweets
        # for tweet in searched_tweets:
        #     # count tweets
        #     pass
        #     # add count to df column?
            
        # for tweet in stream_tweets:
        #     pass
        # # break tweets apart for table
        # for tweet in searched_tweets, stream_tweets:
        #     all_tweets["tweet_id"] = tweet['id']

        #     # add all tweets to database! via mogrify

        #     # put tweets in df
        #     self.all_tweets_df = pd.DataFrame.from_dict(all_tweets, columns=[
        #                                               "tweet_id", "user_id", "location", "createdAt", "tweet_text"])

        #     self.all_tweets_df.set_index("tweet_id")

        #     # tweets mention count to news df column
        #     news_instance.all_news_df["tweet_mention_count"] = self.all_tweets_df["tweet_id"].apply(
        #         np.count_nonzero)

            # clear dataframe?
    
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
                        assert (type(tweet) ==
                                str), "Tweet must be converted to JSON string"
                        tweet = json.loads(tweet)  # tweet to dict
                        assert (
                            type(tweet) == dict), "Tweet must be converted from JSON string to type dict"
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

                  #return result


# define stream listener class
class TwitterStreamListener(tweepy.Stream):
    def __init__(self, api=None):
        super(tweepy.Stream, self).__init__()
        self.num_tweets = 0
        # self.file = open('tweets.txt', 'w')
        # self.db = ''
        self.tweet_list = []
        # self.file = open("tweets.json", "w")

    def on_status(self, status): # TODO just want to collect tweets from the stream then call the cleaner on them outside of the class instance
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


