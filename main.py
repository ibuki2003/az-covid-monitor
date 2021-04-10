from bs4 import BeautifulSoup
import urllib
import base64
import twitter
import config
import sqlite3


AUTH_TOKEN = 'Basic ' + \
    base64.b64encode(bytes(config.USERNAME + ':' +
                           config.PASSWORD, 'ascii')).decode('ascii')
BASE_URL = 'https://www.azabu-jh.ed.jp/gakunai/'
GRADE_NAMES = {
    'all_students': '全校',
    '2021': '新M1',
    '2020': '新M2',
    '2019': '新M3',
    '2018': '新H1',
    '2017': '新H2',
    '2016': '新H3',
}

NEW_PAGE_TPL = '{grade}向け: 「{title}」が追加されました'
UPD_PAGE_TPL = '{grade}向け: 「{title}」が更新されました'


def main():
    db = Database()
    for grade in GRADE_NAMES:
        get_url = BASE_URL + grade + '/'

        try:
            req = urllib.request.Request(get_url, None, {
                'Authorization': AUTH_TOKEN
            })
            with urllib.request.urlopen(req) as res:
                links = get_links(res.read())

        except Exception as e:
            print(e)
            continue

        for link in links:
            req = urllib.request.Request(link[0], None, {
                'Authorization': AUTH_TOKEN
            })
            with urllib.request.urlopen(req) as res:
                cur_upd = res.headers['last-modified']
                old_upd = db.get_last_update(link[0])
                if old_upd is None:
                    twitter.tweet(NEW_PAGE_TPL.format(
                        grade=GRADE_NAMES[grade], title=link[1]))
                    print("new: ", grade, link[1], cur_upd)
                elif old_upd != cur_upd:
                    twitter.tweet(UPD_PAGE_TPL.format(
                        grade=GRADE_NAMES[grade], title=link[1]))
                    print("upd: ", grade, link[1], old_upd, cur_upd)
                db.set_last_update(link[0], cur_upd)


def get_links(html):
    soup = BeautifulSoup(html, 'lxml')
    return [
        (
            elm['href'],
            elm.find('dd', class_="text").find(text=True))
        for elm in soup
        .find('ul', class_='topicsInfo')
        .find_all('a', href=True)]


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.c = self.conn.cursor()
        try:
            res = self.c.execute('select * from tbl')
        except:
            self.c.execute('create table tbl (url integer, updated text)')
            self.conn.commit()

    def __del__(self):
        self.c.close()
        self.conn.close()

    def get_last_update(self, url):
        res = self.c.execute(
            'select updated from tbl where url=?', (url,)).fetchone()
        if res is None:
            self.c.execute(
                'insert into tbl (url, updated) values (?, ?)', (url, ''))
            self.conn.commit()
            return None
        return res[0]

    def set_last_update(self, url, updated):
        self.get_last_update(url)  # create line if not exist
        self.c.execute('update tbl set updated=? where url=?', (updated, url,))
        self.conn.commit()


if __name__ == "__main__":
    main()
