import requests
import urllib.parse
import re
import time

import logging
log = logging.getLogger("crossword_logger")

from clue_models.base_clue_solver import ClueSolver


class WebSolver(ClueSolver):
    """
    searches website 'wordplays.com' for clue
    collects top k results
    """
    MODEL_NAME = 'web'

    BASE_URL = 'https://www.wordplays.com/crossword-solver/'
    USE_PROXY = False
    PROXIES = {'http': 'socks5://user:pass@host:port',
               'https': 'socks5://user:pass@host:port'} if USE_PROXY else {}
    TIMEOUT = 5
    SLEEP_TIME = 0.2
    SEARCH_STRING = '<a href="/crossword-clues/'
    GOT_BANNED = '<!DOCTYPE html>\n<html lang="" prefix="og: http://ogp.me/ns#" >\n<head>\n<title>Contact Wordplays.com'

    def __init__(self, entries, puzname, num_candidates_per_entry=None, load=True, save=True):
        super().__init__(num_candidates_per_entry=num_candidates_per_entry, load=load, save=save)
        self.banned = False
        self.generate_candidates(entries, puzname)

    def find_clue(self, entry):
        if self.banned:
            return self.ERROR

        log.info(f"\nlooking for answer for clue: {entry['clue']}")

        length = entry['length']
        clue = urllib.parse.quote(entry['clue'])
        url = self.BASE_URL + clue
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5'}, proxies=self.PROXIES, timeout=self.TIMEOUT)
        except:
            log.info("connection error!  probably got banned!")
            self.banned = True
            return self.ERROR

        text = r.text
        if r.text.startswith(self.GOT_BANNED):
            log.info("got banned!")
            self.banned = True
            return self.ERROR

        out = []
        for s in re.finditer(self.SEARCH_STRING, text):
            i = s.end()
            word = []
            while text[i] != '"':
                word.append(text[i])
                i += 1
            if len(word) != length:
                continue
            out.append(''.join(word).upper())
            if len(out) == self.num_candidates_per_entry:
                break
        log.info(f"found candidates: {out}")

        time.sleep(self.SLEEP_TIME)
        return out

if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    logging.basicConfig()

    model = WebSolver()
    model({'clue': 'What are you?', 'length': 6})
