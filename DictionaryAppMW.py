import os
from pathlib import Path

from DictionaryApp import DictionaryApp

class DictionaryAppMW(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.merriam-webster.com/dictionary"
        self.cacheDir = Path(os.environ.get('HOME')) / '.mwdic_cache'
