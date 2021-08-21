from TikTokApi import TikTokApi
# pip install TikTokApi --upgrade
from proto_pipeline import keywords
import configparser
import json
import pandas as pd
from timer import Timer

tiktok_config = configparser.ConfigParser()
tiktok_config.read('config.ini')

fp = tiktok_config['tiktokAuth']['s_v_web_id']

# instantiate class

tiktoks = TikTokApi.get_instance(custom_verifyFp=fp, use_test_endpoints=True)

class TikToks(TikTokApi):
    def __init__(self):
        super(TikTokApi, self).__init__()
        self.tiktok_list = []

    @Timer("Tiktok Download")
    def get_tiktok_trends(self):
        # returns tiktok dictionary/JSON
        self.api = TikTokApi()
        trends = self.api.by_hashtag(keywords)

        with open("tiktoks.json", "w") as f:
            json.dump(trends, f)

        with open("tiktoks.json", "r") as file:
            toks_json = file.read().split("\n")

            for tok in toks_json:
                tok_obj = json.loads(tok)
                
                if 'id' in tok:
                    tok_obj['userID'] = tok_obj['author']['id']
                    tok_obj['postID'] = tok_obj['id']
                if 'signature' in tok:
                    tok_obj['user_bio'] = tok_obj['author']['signature']
                if 'challenges' in tok:
                    # iterate over multiples
                    tok_obj['tagID'] = tok_obj['challenges']['id']
                    tok_obj['tag_name'] = tok_obj['challenges']['title']
                if 'createTime' in tok:
                    tok_obj['createTime'] = tok_obj['createTime']
                if 'desc' in tok:
                    tok_obj['description'] = tok_obj['desc']
                if 'stats' in tok:
                    tok_obj['comment_count'] = tok_obj['stats']['commentCount']
                    tok_obj['digg_count'] = tok_obj['stats']['diggCount']
                    tok_obj['play_count'] = tok_obj['stats']['playCount']
                    tok_obj['share_count'] = tok_obj['stats']['shareCount']
                if 'video' in tok:
                    tok_obj['videoID'] = tok_obj['itemList']['video']['id']
                if 'sound' in tok:
                    tok_obj['soundID'] = tok_obj['sound']['id']
                    tok_obj['soundTitle'] = tok_obj['sound']['title']
                    tok_obj['isOriginal'] = tok_obj['sound']['original']
                if 'music' in tok:
                    tok_obj['songID'] = tok_obj['music']['id']
                    tok_obj['songTitle'] = tok_obj['music']['title']
                
                self.tiktok_list.append(tok_obj)

            self.toks_df = pd.DataFrame(self.tiktok_list)

            # split df by columns corresponding to tables

        return self.toks_df

