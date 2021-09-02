from TikTokAPI import TikTokAPI
import configparser
import nest_asyncio
import pandas as pd
import psycopg2

from news import *
from database import *

# nest_asyncio.apply()
# __import__('IPython').embed()

# {'statusCode': 0,
#     'challengeInfo': {'challenge': {'id': '245733', 'title': 'jeopardy', 'desc': '', 'profileThumb': '', 'profileMedium': '', 'profileLarger': '', 'coverThumb': '', 'coverMedium': '', 'coverLarger': '', 'isCommerce': False, 'splitTitle': 'jeopardy'},
#     'stats': {'videoCount': 9833, 'viewCount': 179900000},
#     'challengeAnnouncement': {'body': '', 'title': ''}},
#     'shareMeta': {'title': '#jeopardy on TikTok', 'desc': '179.0m views - Watch awesome short videos created with trending hashtag #jeopardy'}
#     }

c = configparser.ConfigParser()
c.read('sm-political-analysis/config.ini')

host = c['database']['host']
username = c['database']['user']
password = c['database']['password']
db = c['database']['database']

news_api_key = c['newsAuth']['api_key']
tiktok_sv_id = c['tiktokAuth']['s_v_web_id']
tiktok_tt_id = c['tiktokAuth']['tt_webid']

tiktok_auth = {
    "s_v_web_id": tiktok_sv_id,  # references variables saved from config file
    "tt_webid": tiktok_tt_id
}

class TikTokAPI(TikTokAPI):

    # create db connection for mogrify
    # DATABASE = DataBase(host, username, password)
    # CXN = DATABASE.create_db_connection(db)

    def __init__(self, cookie, logger=logging, api=None):
        super(TikTokAPI, self).__init__()
        self.cookie = cookie
        self.tiktok_count = 0
        self.logger = logging.basicConfig(filename='tiktok.log', filemode='w',
                                          format=f'%(asctime)s - %(levelname)s - %(message)s')
    def getVideosByHashtag(self, hashtags, count=3000):
        try:
            for hashTag in hashtags:
                try:
                    hashTag = hashTag.replace("#", "")
                    hashTag_obj = self.getHashTag(hashTag)
                    hashTag_id = hashTag_obj["challengeInfo"]["challenge"]["id"]
                except (KeyError, ReferenceError) as err:
                    logging.error(err)
                    continue
                else:
                    url = self.base_url + "/challenge/item_list/"
                    req_default_params = {
                        "secUid": "",
                        "type": "3",
                            "minCursor": "0",
                            "maxCursor": "0",
                            "shareUid": "",
                            "recType": ""
                        }
                    params = {
                        "challengeID": str(hashTag_id),
                            "count": str(count),
                            "cursor": "0",
                        }
                    for key, val in req_default_params.items():
                            params[key] = val
                    for key, val in self.default_params.items():
                            params[key] = val
                    extra_headers = {
                            "Referer": "https://www.tiktok.com/tag/" + str(hashTag)}
                    self.tiktok_count += 1
                    tok = self.send_get_request(url, params, extra_headers=extra_headers)
                    # write tiktoks to json file
                    with open("tiktoks.json", "a") as f:
                        json.dump(tok, f)
                    print(self.tiktok_count)
                    return tok
        except KeyboardInterrupt as ex:
            raise ex
        finally: # TODO do we need a df?
            self.tiktok_df = pd.read_json('tiktoks.json') # columns=['postID', 'createTime', 'userID', 'description', 'musicId', 'soundId', 'tags'])
            logging.info(f'This run scraped {self.tiktok_count} TikToks')
            return self.tiktok_df
            # DATABASE.execute_mogrify(CXN, tiktok_df, )
            # return tiktok_df
            # TODO mogrify into database


# Insert Tweet data into database
    def dbConnect(user_id, user_name, tweet_id, tweet, retweet_count, hashtags):
        """Insert tiktok objects into database directly without intermediary dataframe"""
        self.from_file = "sm-political-analysis/tiktoks.json"
        conn = psycopg2.connect(host="localhost", database="TwitterDB", port=5432, user= < user > , password= < password > )

        cur = conn.cursor()

        # insert user information
        command = '''INSERT INTO TwitterUser (user_id, user_name) VALUES (%s,%s) ON CONFLICT
                    (User_Id) DO NOTHING;'''
        cur.execute(command, (user_id, user_name))

        # insert tweet information
        command = '''INSERT INTO TwitterTweet (tweet_id, user_id, tweet, retweet_count) VALUES (%s,%s,%s,%s);'''
        cur.execute(command, (tweet_id, user_id, tweet, retweet_count))

        # insert entity information
        for i in range(len(hashtags)):
            hashtag = hashtags[i]
            command = '''INSERT INTO TwitterEntity (tweet_id, hashtag) VALUES (%s,%s);'''
            cur.execute(command, (tweet_id, hashtag))

        # Commit changes
        conn.commit()

        # Disconnect
        cur.close()
        conn.close()

# instantiate news class
# news = News(news_api_key)
# news_df = news.get_all_news() # TODO assert that df has information in it

# # instantiate TikTok API
# api = TikTokAPI(cookie=tiktok_auth)
# api.tiktok_df = news_df['keywords'].map(api.getVideosByHashtag)




