import numpy as np
from sqlalchemy import create_engine
import logging
import psycopg2
from psycopg2 import Error
import configparser
from timer import Timer

c = configparser.ConfigParser()
c.read('config.ini')

# config credentials
host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['database']


# class dbSetup:

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


def create_database(connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            logging.info("Database created successfully")
        except Error as err:
            logging.error(f"Error: '{err}'")


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

@Timer(name='Query Execution')
def execute_query(connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            logging.info("Query successful")
        except Error as err:
            print(f"Error: '{err}'")

    # connect to server
server = create_server_connection(host, username, password)

create_database_query = """
        CREATE DATABASE IF NOT EXISTS sm_news; 
    """
    # create necessary tables
    # keyWords VARCHAR
create_article_table = """
    CREATE TABLE IF NOT EXISTS articles (
        publishedAt DATE,
        title VARCHAR PRIMARY KEY,
        author VARCHAR,
        url TEXT
        );
    """    
create_article_table_index = """
    CREATE INDEX index 
        ON articles(publishedAt, 
            title
        );
    """
create_article_text_table = """
    CREATE TABLE IF NOT EXISTS article_text (
        title VARCHAR PRIMARY KEY REFERENCES articles (title),
        text
        );
    """
create_article_text_table_index = """
    CREATE INDEX index 
        ON article_text(publishedAt, title
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


def read_query(connection, query):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as err:
            print(f"Error: '{err}'")

@Timer(name='Mogrify')
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
