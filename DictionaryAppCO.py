import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp

class DictionaryAppCO(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.collinsdictionary.com/dictionary/english"
        self.cacheDir = Path(os.environ.get('HOME')) / '.mwdic_cache'

    def processLines(self):
        ols = self.lines

        def delFromRegex(ls, r):
            
            
        
        for flt in (rmScum,): ols = flt(ols)
        self.outputLines = list(ols)
