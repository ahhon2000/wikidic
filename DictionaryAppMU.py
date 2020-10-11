import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp
from EasyPipe import Pipe

class DictionaryAppMU(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = None
        self.cacheDir = None
        self.dictionaryAppOX = None

    def phraseIsCached(self):
        return True

    def getCacheFile(self):
        return None

    def loadCached(self):
        p = Pipe(['dict', self.phrase])
        (out, emsg, st) = (p.stdout, p.stderr, p.status)
        if p.status:
            from DictionaryAppOX import DictionaryAppOX
            ox = DictionaryAppOX(clArgs=self.clArgs)
            self.dictionaryAppOX = ox
            result = ox.run(output=False)
            out = result['text']

            self.dlAttempt = ox.dlAttempt

        self.lines = out.split("\n")

    def download(self):
        if not self.options.redownload:
            raise Exception('this method can only be called with redownload=True')
