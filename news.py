"""Compute weight of words in articles and titles"""

from django.db import DatabaseError
from get_news import *
import requests
from bs4 import BeautifulSoup
from database import *
import logging
from keywords import *

# https://towardsdatascience.com/tf-idf-for-document-ranking-from-scratch-in-python-on-real-world-dataset-796d339a4089 

#create dataframe?
article_text_df = pd.DataFrame({'index': '',
                             'title': '',
                             'text': ''
                            })

# execute query to create corresponding table in db
connection = create_db_connection(c['database']['host'],
                                  c['database']['user'],
                                  c['database']['password'],
                                  c['database']['database'])
try:
    execute_query(connection, create_article_text_table)
except (DatabaseError, ConnectionError) as e:
    logging.error({e}, ': please check article_text table and functions ')
else:
    execute_mogrify(connection, article_text_df, 'article_text')


def get_text(url): 
    """Get article text using Requests and BeautifulSoup"""
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html)
    soup.get_text()


#* CREATE A KEY BASED ON THE WORD MASH?
# apply get_text function using urls from all_news df
url_text = all_news['url'].apply(
    lambda row: get_text(all_news['url']),
    axis=1
)

# put text into df
article_text_df['text'] = url_text

#* extract keywords from text to new df column
# article_text_df['keys'] = keyword_extraction(article_text)
keywords = article_text_df['keywords'].apply(
    lambda row: get_top_n(tf_idf_score, 3) # looks like i'm gonna have to create a class ughhhh
)

# append text and keys to database
execute_mogrify(connection, article_text_df, 'article_text')

# add 3 columns to df/db -> same number of keywords (3) everytime + can rank by importance w kw1 kw2 kw3 in KEYWORDS.py
## combine columns into list/iterable 
## combination generator -> search for any combination of the top three words on twitter and tiktok
# decorator to make results an iterable?