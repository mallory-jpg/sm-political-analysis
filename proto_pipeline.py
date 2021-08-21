from timer import Timer
from database import *
from get_news import *
from tweets import *
import configparser
import psycopg2

# configure ConfigParser
c = configparser.ConfigParser()
c.read('config.ini')

# .config credentials
host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['database']

news_api_key = c['newsAuth']['api_key']
tiktok_id = c['tiktokAuth']['s_v_web_id']

# .config twitter credentials
access_token = c['twitterAuth']['access_token']
access_token_secret = c['twitterAuth']['access_token_secret']
consumer_key = c['twitterAuth']['consumer_key']
consumer_secret = c['twitterAuth']['consumer_secret']

# instantiate DataBase class using .config files
postgres_db = DataBase(host, username, password)
# instantiate News class
news = News(news_api_key)
# instantiate Tweet Stream Listener
listener = TwitterStreamListener()
# instantiate authentication
tweets = Tweets(consumer_key, consumer_secret, access_token, access_token_secret)
auth = tweets.tweepy_auth()
# authenticate stream
tweet_stream = tweepy.Stream(auth, listener)

# connect to server
postgres_server = postgres_db.create_server_connection()

# connect to social media news db
connection = postgres_db.create_db_connection(db)

# setup tables
try:
    postgres_db.execute_query(connection, create_article_table)
    postgres_db.execute_query(connection, create_article_text_table)
    postgres_db.execute_query(connection, create_batch_tweets_table)
    postgres_db.execute_query(connection, create_stream_tweets_table)
    postgres_db.execute_query(connection, create_tweet_trends_table)
    postgres_db.execute_query(connection, create_political_event_table)

    postgres_db.execute_query(connection, create_tiktok_sounds_table)
    postgres_db.execute_query(connection, create_tiktok_music_table)
    postgres_db.execute_query(
    connection, create_tiktok_stats_table)  # not running?
    postgres_db.execute_query(connection, create_tiktok_tags_table)
    postgres_db.execute_query(connection, create_tiktoks_table)
except (DatabaseError, ConnectionError) as e:
    logging.error({e}, 'Check SQL queries')

# news.request_pop_news()
# news.get_top_headlines()

# apply get_text function using urls from all_news df
url_text = news.all_news_df['url'].apply(
        lambda row: news.article_text(news.all_news_df['url']),
        axis=1)
# put url_text into df
news.article_text_df['text'] = url_text

# get keywords from article text
# get top 3 words of significance
keywords = news.article_text_df['keywords'].apply(
    lambda row: news.get_top_n(news.tf_idf_score, 3)
)

# TODO test get_news & find order of key:value pairs
news.article_text_df['keyword1'] = keywords[1]
news.article_text_df['keyword2'] = keywords[2]
news.article_text_df['keyword3'] = keywords[3]

# filter tweet stream?
filtered_stream = tweet_stream.filter(track=[keywords])
# mogrify stream
postgres_db.execute_mogrify(connection, filtered_stream, 'stream_tweets')

# tweet search
search = tweets.tweet_search(query={
    'tweet.fields': 'attachments,author_id,created_at,geo,id,public_metrics,source,text',
    'expansions': 'geo.place_id,attachments.media_keys', 'place.fields': 'country,geo,id,name', 'user.fields': 'created_at,description,id,location,name,username,verified'})
# change to datetime
tweets.tweet_search_df['created_at'].apply(
    lambda row: datetime.strptime(
        row, '%Y-%m-%d %H:%M:%S'),  # TODO check formatting
    axis=0)
# count keywords in tweet search df 
batch_tweets = tweets.tweet_search_df['text'].str.contains(
    keywords, case=False)
# mogrify tweets with keywords 
postgres_db.execute_mogrify(connection, batch_tweets, 'batch_tweets')

# tweet trends
tweet_trends = tweets.tweet_trends()
# mogrify trends
postgres_db.execute_mogrify(connection, tweet_trends, 'tweet_trends')

# execute mogrify - insert news into database
postgres_db.execute_mogrify(connection, news.all_news_df, 'articles')
# append text and keys to database
postgres_db.execute_mogrify(connection, news.article_text_df, 'article_text')
