import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp

class DictionaryAppMW(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.merriam-webster.com/dictionary"
        self.cacheDir = Path(os.environ.get('HOME')) / '.mwdic_cache'

    def processLines(self):
        ols = self.lines

        def flt1(ls):
            for i, l in enumerate(ls):
                if re.search(r'^[^\s]', l): return ls[i:]
            return []

        def flt2(ls):
            for i, l in enumerate(ls):
                if re.search(r'^\s*Dictionary Entries near', l): return ls[0:i]
            return ls
        
        for flt in (flt1, flt2): ols = flt(ols)
        self.outputLines = list(ols)
