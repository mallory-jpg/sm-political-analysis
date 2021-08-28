import numpy as np
# from sqlalchemy import create_engine
import logging
import psycopg2
from psycopg2 import Error
import configparser
from timer import Timer

# create db
create_database_query = """
        CREATE DATABASE IF NOT EXISTS sm_news;
    """
# create necessary tables
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
        title VARCHAR PRIMARY KEY,
        article_text TEXT
        );
    """
create_political_event_table = """
    CREATE TABLE IF NOT EXISTS event (
        eventID ID PRIMARY KEY,
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
        userID VARCHAR NOT NULL,
        tweet VARCHAR NOT NULL,
        location VARCHAR NOT NULL,
        tags VARCHAR NOT NULL
        );
    """
create_tiktoks_table = """
    CREATE TABLE IF NOT EXISTS tiktoks (
        postID INT PRIMARY KEY,
        createTime DATE NOT NULL,
        userID INT NOT NULL,
        description VARCHAR NOT NULL,
        musicID INT NOT NULL,
        soundID INT NOT NULL,
        tags VARCHAR NOT NULL
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
        postID INT PRIMARY KEY,
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

# add foreign keys
alter_tiktoks_table = """
    ALTER TABLE tiktoks
    ADD FOREIGN KEY(musicID) REFERENCES tiktok_music(songID),
    ADD FOREIGN KEY(soundID) REFERENCES tiktok_sounds(soundID),
    ADD FOREIGN KEY(userID) REFERENCES users(userID)
    ON DELETE SET NULL;
"""
alter_tiktok_stats_table = """
    ALTER TABLE tiktok_stats
    ADD FOREIGN KEY(postID) REFERENCES tiktoks(postID)
    ON DELETE SET NULL;
"""


class DataBase():
    def __init__(self, host_name, user_name, user_password):
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password

    def create_server_connection(self):
        self.connection = None
        try:
            self.connection = psycopg2.connect(
                host=self.host_name,
                user=self.user_name,
                password=self.user_password
            )
            logging.info("Database connection successful")
        except Error as err:
            logging.error(f"Error: '{err}'")

        return self.connection

    def create_database(self, connection, query):
        self.connection = connection
        cursor = connection.cursor()
        try:
                cursor.execute(query)
                logging.info("Database created successfully")
        except Error as err:
                logging.error(f"Error: '{err}'")

    def create_db_connection(self, db_name):
        self.db_name = db_name
        self.connection = None
        try:
                self.connection = psycopg2.connect(
                    host=self.host_name,
                    user=self.user_name,
                    password=self.user_password,
                    database=self.db_name
                )
                # cursor = connection.cursor()
                logging.info("PostgreSQL Database connection successful")
        except Error as err:
                logging.error(f"Error: '{err}'")

        return self.connection

    @Timer(name='Query Execution')  # *TODO fix __enter__ attribute error
    def execute_query(self, connection, query):
        self.connection = connection
        cursor = connection.cursor()
        try:
                cursor.execute(query)
                self.connection.commit()
                logging.info("Query successful")
        except Error as err:
                print(f"Error: '{err}'")

    def read_query(self, connection, query):
        self.connection = connection
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as err:
            logging.error(f"Error: '{err}'")

    @Timer(name='Mogrify')
    def execute_mogrify(self, conn, df, table):
        """
        Using cursor.mogrify() to build the bulk insert query
        then cursor.execute() to execute the query
        """
        self.connection = conn
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

