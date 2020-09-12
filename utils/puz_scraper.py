"""
Downloads puz files from the internet

PROBLEM: current best source seems to be NYT, but they require authorization
 -> look for other sources later
 -> for now just download a bunch manually

"""


BASE_URL = 'https://www.nytimes.com/svc/crosswords/v2/puzzle/daily-'

import requests

def get_from_dates(start_date, end_date):

    for single_date in daterange(start_date, end_date):
        # try:
        # TODO: not finding urls for some reason, fix later (think need username for NYT)
        url = BASE_URL + str(single_date) + '.puz'
        url = 'https://www.wordplays.com/crossword-solver/hello'
        print(f"trying {url}...")

        r = requests.get(url, headers={'User-Agent': 'Mozilla/5'})

        print(r.status_code)
        with open('./test.txt', 'wb') as f:
            f.write(r.content)

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
    start_date = date(2020, 5, 25)
    end_date = date(2020, 7, 29)
    get_from_dates(start_date, end_date)