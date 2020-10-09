import os
import argparse
import pydoc
import re

from EasyPipe import Pipe

class DictionaryApp:
    def __init__(self, clArgs=[], pager='less'):
        self.clArgs = list(clArgs)
        self.options = None

        self.pager = pager
        self.phrase = ''
        self.urlBase = ''
        self.cacheDir = None   # should be a Path object
        self.lines = []
        self.outputLines = []

        self._parseCLArgs()

    def _parseCLArgs(self):
        argp = argparse.ArgumentParser()

        argp.add_argument('-n', '--no-less', action="store_true", help="Do not use pager (less)")
        argp.add_argument('-r', '--redownload', action="store_true", help="Redownload article if cache is empty")
        argp.add_argument("arguments", nargs='*')

        print("debug", self.clArgs)
        opt = argp.parse_args(self.clArgs[1:])

        self.options = opt

        p = " ".join(opt.arguments)
        p = re.sub(r'\s{2,}', r' ', p.strip())
        self.phrase = p

    def phraseIsCached(self):
        f = self.cacheDir / self.phrase
        return f.exists()

    def outputIsEmpty(self):
        return all(re.search(r'^\s*$', l) for l in self.outputLines)

    def loadCached(self):
        f = self.cacheDir / self.phrase
        print('debug f =', f)
        with f.open() as fp:
            self.lines = list(map(lambda l: re.sub(r"\n+$", r'', l), fp))

    def output(self):
        if not self.pager or self.options.no_less:
            # without a pager
            for l in self.outputLines:
                print(l)
        else:
            # with a pager
            t = "".join(l + "\n" for l in self.outputLines)
            oldpager = os.environ.get('PAGER', '')
            pydoc.pager(t)
            os.environ['PAGER'] = oldpager

    def processLines(self):
        self.outputLines = list(self.lines)

    def download(self):
        pass
        
    def run(self):
        flgCached = self.phraseIsCached()
        if flgCached:
            self.loadCached()
            self.processLines()

        if any((
            not flgCached,
            self.outputIsEmpty() and self.options.redownload,
        )):
            self.download()
            self.processLines()

        self.output()
