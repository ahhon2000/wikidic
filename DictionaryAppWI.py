import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp, delLines, copyLines

class DictionaryAppWI(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "http://en.wiktionary.org/wiki"
        self.cacheDir = Path(os.environ.get('HOME')) / '.wikidic_cache'

    def processLines(self):
        ols = self.lines

        emptyMarkers = re.compile(r'^\s*Wiktionary does not yet have an entry for')
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
            lambda ls: delLines(ls, r'^Contents\b', r'^[^\s]'),
            lambda ls: delLines(ls, r'^Translation', r'^[^\s]'),
            lambda ls: delLines(ls, r'^Navigation menu', None),
            lambda ls: delLines(ls, r'^Anagrams', r'^[^\s]'),
            lambda ls: delLines(ls, r'^Statistics', r'^[^\s]'),
            lambda ls: delLines(ls, r'^Related terms', r'^[^\s]'),
            lambda ls: delLines(ls, r'^Derived terms', r'^[^\s]'),
        ):
            ols = flt(ols)

        ols = list(ols)
        self.outputLines = [] if flgEmpty else ols
