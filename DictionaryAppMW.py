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
        
        for flt in (
            lambda ls: copyLines(ls, r'^[^\s]', None),
            lambda ls: delLines(ls, r'^\s*Dictionary Entries near', None),
        ):
            ols = flt(ols)

        self.outputLines = list(ols)
