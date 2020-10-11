import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp, delLines, copyLines

class DictionaryAppMW(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.merriam-webster.com/dictionary"
        self.cacheDir = Path(os.environ.get('HOME')) / '.mwdic_cache'

    def processLines(self):
        ols = self.lines

        emptyMarkers = re.compile(r"^\s*The word you've entered isn't in the dictionary")
        flgEmpty = False
        def detectEmptyArticle(ls):
            nonlocal emptyMarkers, flgEmpty
            for l in ls:
                if emptyMarkers.search(l):
                    flgEmpty = True
                    break
                yield l
        
        for flt in (
            lambda ls: detectEmptyArticle(ls),
            lambda ls: copyLines(ls, r'^[^\s]', None),
            lambda ls: delLines(ls, r'^\s*Dictionary Entries near', None),
            lambda ls: delLines(ls, r'^\s*\[[0-9]*\]Save\s+Word\s*$'),
            lambda ls: delLines(ls, r'^\s*Log In\s*$'),
            lambda ls: delLines(ls, r'^\s*To save this word, you.ll need to log in'),
            lambda ls: delLines(ls, r'^\s*SAVED WORDS.*\bview recents\b\s*$'),
            lambda ls: delLines(ls, r'^\s*References\s*$', None),
        ):
            ols = flt(ols)

        ols = list(ols)
        self.outputLines = [] if flgEmpty else ols
