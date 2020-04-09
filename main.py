from bs4 import BeautifulSoup
import urllib
import requests
import json
import base64
import datetime
import twitter
import config


AUTH_TOKEN = 'Basic ' + base64.b64encode(bytes(config.USERNAME + ':' + config.PASSWORD, 'ascii')).decode('ascii')
BASE_URL = 'https://www.azabu-jh.ed.jp/schoollife/topics/gakunai/covid-19/'
URLS = {
    'M2': 'jh1',
    'M3': 'jh2',
    'H1': 'jh3',
    'H2': 'sh1',
    'H3': 'sh2',
    'M1': 'sh3',
}

for page in URLS:
    get_url = BASE_URL + URLS[page]

    req = urllib.request.Request(get_url, None, {
        'Authorization': AUTH_TOKEN
    })
    with urllib.request.urlopen(req) as res:
        soup = BeautifulSoup(res.read(), "lxml")
    now_main = str(soup.find("div", class_ = "main"))
    
    try:
        with open(URLS[page]+'_old.html') as f:
            old_main = f.read()
    except:
        old_main = now_main

    if now_main != old_main:
        print(page, 'updated@', datetime.datetime.now())

        with open(URLS[page]+'_old.html', 'w') as f:
            f.write(now_main)
    
        notify_msg = '新' + page + '向けのお知らせページが更新されました! @ ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        print(notify_msg)
        twitter.tweet(notify_msg)
