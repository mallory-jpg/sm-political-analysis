import pytest
import pytest_mock

# - make sure news keywords are a list
# - make sure auth is verified
# - check for random user agent - dont get Blocked 
# @pytest.mark.database_access to mark - since tweets are being streamed into df

def test_json_conversion(tweet):
    assert (type(tweet) == str), "Tweet must be converted to JSON string"
    assert (type(tweet) == dict), "Tweet must be converted from JSON string to type dict"

def test_tweepy_auth():
    # assert that it exists and gets verified
    pass


@pytest.mark.api_call
def test_tweet_search():
    # assert that api is present and verified
    # make sure API works
    # make sure results of api call are more than 0 -> may need less stringent keywords or something
    pass


@pytest.mark.api_call
def test_twitter_stream():
    # assert that stream exists & works
    # assert that api works
    # make sure stream listener is valid
    # make sure stuff is getting laoded into json file
    pass
