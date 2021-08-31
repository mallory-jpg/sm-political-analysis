from TikTokAPI import TikTokAPI
import configparser
from configparser import ConfigParser

c = configparser.ConfigParser()
c.read('config.ini')

news_api_key = c['newsAuth']['api_key']
tiktok_sv_id = c['tiktokAuth']['s_v_web_id']
tiktok_tt_id = c['tiktokAuth']['tt_webid']

class TikToks(TikTokAPI):

    tiktok_auth = {
        "s_v_web_id": tiktok_sv_id,
        "tt_webid": tiktok_tt_id
    }
    
    def __init__(self, api=None):
            super(TikTokAPI, self).__init__()
            # self.tiktoks_df 
    def getVideosByHashtag(self, hashtags, count=30):
            for hashTag in hashtags:
                hashTag = hashTag.replace("#", "")
                hashTag_obj = self.getHashTag(hashTag)
                hashTag_id = hashTag_obj["challengeInfo"]["challenge"]["id"]
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
                return self.send_get_request(url, params, extra_headers=extra_headers)
