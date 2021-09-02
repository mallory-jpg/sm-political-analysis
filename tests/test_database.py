import pytest
from pytest import MonkeyPatch
import configparser
import psycopg2
from psycopg2 import errorcodes

# Error info: https://www.psycopg.org/docs/errorcodes.html
# error code table: https://www.postgresql.org/docs/current/errcodes-appendix.html#ERRCODES-TABLE

c = configparser.ConfigParser()
c.read('config.ini')

host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['test']


class mockDB():

    @classmethod
    @pytest.fixture(scope='session')
    def setupClass(cls):
        """Define database connection"""
        connection = psycopg2.connect(
            host=host,
            user=username,
            password=password
        )
        cursor = connection.cursor()
    
        # drop db if already exists
        try:
            cursor.execute(f"DROP DATABASE {db}")
            cursor.close()
        except psycopg2.Error as err:
            print(f'{db}{err}')
        else:
            print("Database dropped")
        
        # create new db
        try:
            cursor.execute(f"CREATE DATABASE {db}")
        except psycopg2.Error as err:
            print(f"Creation of {db} database failed: {err}")
            exit(1)
        else:
            connection = psycopg2.connect(
                host=host,
                user=username,
                password=password,
                database=db
            )

        # create mock table
        query = """CREATE TABLE test_table (
            id VARCHAR(30) NOT NULL PRIMARY KEY,
            text_test TEXT NOT NULL,
            int_test INT NOT NULL
        )
        """

        try:
            cursor.execute(query)
            connection.commit()
        except psycopg2.Error as err:
            if err.pgcode == errorcodes.DUPLICATE_TABLE:
                print("test_table already exists")
            else:
                print(err)
        else:
            print("OK")

        # insert data
        insert_data_query = """INSERT INTO test_table (id, text_test, int_test) VALUES
                    ('1', 'test_text_1', 1),
                    ('2', 'test_text_2', 2)
        """
        try:
            cursor.execute(insert_data_query)
            connection.commit()
        except psycopg2.Error as err:
            print(f"Data insertion into test_table failed.\n {err}")
        finally:
            cursor.close()
            connection.close()

        # cls.mock_db_config = MonkeyPatch.setitem(dic=test_config)
        return connection

    @classmethod
    def tearDownClass(cls):
        connection = psycopg2.connect(
            host=host,
            user=username,
            password=password
        )
        cursor = connection.cursor()

        # drop test db
        try:
            cursor.execute(f"DROP DATABASE {db}")
            connection.commit()
            cursor.close()
        except psycopg2.Error as err:
            print(f"Database drop failed: {db} database does not exist.")
        finally:
            connection.close()


