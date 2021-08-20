from timer import Timer
from database import *
from get_news import *
import configparser

# configure ConfigParser
c = configparser.ConfigParser()
c.read('config.ini')

# references .config credentials
host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['database']

news_api_key = c['newsAuth']['api_key']
tiktok_id = c['tiktokAuth']['s_v_web_id']
twitter_api_key = c['twitterAuth']['api_key']

# instantiate DataBase class using .config files
postgres_db = DataBase(host, username, password)

# instantiate News class
news = News(news_api_key)

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

# article_text_df['keys'] = keyword_extraction(article_text)
# get top 3 words of significance
keywords = news.article_text_df['keywords'].apply(
    lambda row: news.get_top_n(news.tf_idf_score, 3)
)

# TODO test get_news & find order of key:value pairs
news.article_text_df['keyword1'] = keywords[1]
news.article_text_df['keyword2'] = keywords[2]
news.article_text_df['keyword3'] = keywords[3]


# execute mogrify - insert news into database
postgres_db.execute_mogrify(connection, news.all_news_df, 'articles')

# append text and keys to database
postgres_db.execute_mogrify(connection, news.article_text_df, 'article_text')
