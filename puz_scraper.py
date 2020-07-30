"""
Downloads puz files from the internet

PROBLEM: current best source seems to be NYT, but they require authorization
 -> look for other sources later
 -> for now just download a bunch manually

"""


BASE_URL = 'https://www.nytimes.com/svc/crosswords/v2/puzzle/daily-'

import requests
from requests.auth import HTTPDigestAuth
from requests_oauthlib import OAuth1


# import urllib.request
# req = urllib.request.Request('http://www.example.com/')
# req.add_header('Referer', 'http://www.python.org/')
# # Customize the default User-Agent header value:
# req.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
# r = urllib.request.urlopen(req)

def get_from_dates(start_date, end_date):

    for single_date in daterange(start_date, end_date):
        # try:
        # TODO: not finding urls for some reason, fix later
        url = BASE_URL + str(single_date) + '.puz'
        print(f"trying {url}...")

        #
        # auth = OAuth1('YOUR_APP_KEY', 'YOUR_APP_SECRET',
        # 'USER_OAUTH_TOKEN', 'USER_OAUTH_TOKEN_SECRET')
        # r = requests.get(url)
        # print(r.status_code)
        # import IPython
        # IPython.embed()
        # exit(1)
        #
        # with open('./puzzles/nyt_' + str(single_date) + '.puz', 'wb') as f:
        #     f.write(r.content)
        #     print(f'downloaded puzzle daily-{single_date}!')
        #     # except:
        #     #     print(f'puzzle daily-{single_date} not found!')

from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

if __name__ == '__main__':
    start_date = date(2020, 5, 25)
    end_date = date(2020, 7, 29)
    get_from_dates(start_date, end_date)