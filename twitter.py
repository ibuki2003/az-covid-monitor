import config
import requests_oauthlib
import datetime

def get_session():
    return requests_oauthlib.OAuth1Session(
        config.ConsumerKey,
        config.ConsumerSecret,
        config.AccessToken,
        config.AccessSecret)

TWEET_URL = 'https://api.twitter.com/1.1/statuses/update.json'
def tweet(content):
    content += datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
    data = {
        'status': content
    }

    req = get_session().post(TWEET_URL, params = data)
    return req.status_code == 200
