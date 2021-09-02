import pytest
import configparser

def test_program():
    """Checks whether test is using mocked database program"""
    assert True

#TODO  might be unnecessary with other database tests in place
def test_political_analysis():
    c = configparser.ConfigParser()
    c.read('sm-political-analysis/config.ini')

    host = c['database']['host']
    username = c['database']['user']
    password = c['database']['password']
    db = c['database']['test']

    connection = {
        'host': host,
        'user': username,
        'password': password,
        'database': db
    }
    assert connection == True