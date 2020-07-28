BASE_URL = 'https://www.nytimes.com/svc/crosswords/v2/puzzle/daily-'

import requests
from requests.auth import HTTPBasicAuth

def get_from_dates(start_date, end_date):

    for single_date in daterange(start_date, end_date):
        # try:
        # TODO: not finding urls for some reason, fix later
        url = BASE_URL + str(single_date) + '.puz'
        print(f"trying {url}...")
        r = requests.get(url, auth=HTTPBasicAuth('user', 'pass'))
        print(r.status_code)
        import IPython
        IPython.embed()
        exit(1)

        with open('./puzzles/nyt_' + str(single_date) + '.puz', 'wb') as f:
            f.write(r.content)
            print(f'downloaded puzzle daily-{single_date}!')
            # except:
            #     print(f'puzzle daily-{single_date} not found!')

from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

if __name__ == '__main__':
    start_date = date(2020, 7, 25)
    end_date = date(2020, 7, 29)
    get_from_dates(start_date, end_date)