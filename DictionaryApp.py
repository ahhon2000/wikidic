import os, sys
import argparse
import pydoc
import re

from EasyPipe import Pipe

DFLT_TIMEOUT_SECONDS = 25

def _delCopyLines(ls, addr1, addr2, mode=None):
    if mode not in ('copy', 'delete'): raise Exception('unsupported mode')

    if addr2 is None: addr2 = len(ls) - 1

    ols = []
    flgDel = False if mode == 'delete' else True
    for i, l in enumerate(ls):
        if any((
            isinstance(addr1, int) and i == addr1,
            not isinstance(addr1, int) and re.search(r'' + addr1, l),
        )):
            flgDel = True if mode == 'delete' else False

        if not flgDel: ols += [l]

        if any((
            isinstance(addr2, int) and i == addr2,
            not isinstance(addr2, int) and re.search(r'' + addr2, l),
        )):
            flgDel = False if mode == 'delete' else True

    return ols

def delLines(ls, addr1, addr2):
    return _delCopyLines(ls, addr1, addr2, mode='delete')

def copyLines(ls, addr1, addr2):
    return _delCopyLines(ls, addr1, addr2, mode='copy')


class DictionaryApp:
    def __init__(self, clArgs=[], pager='less'):
        self.clArgs = list(clArgs)
        self.options = None

        self.pager = pager
        self.phrase = ''
        self.urlBase = ''
        self.cacheDir = None   # should be a Path object
        self.dlAttempt = False
        self.lines = []
        self.outputLines = []

        self.timeout_seconds = DFLT_TIMEOUT_SECONDS

        self._parseCLArgs()

    def _parseCLArgs(self):
        argp = argparse.ArgumentParser()

        argp.add_argument('-n', '--no-less', action="store_true", help="Do not use pager (less)")
        argp.add_argument('-r', '--redownload', action="store_true", help="Redownload article if cache is empty")
        argp.add_argument("arguments", nargs='*')

        opt = argp.parse_args(self.clArgs[1:])

        self.options = opt

        p = " ".join(opt.arguments)
        p = re.sub(r'\s{2,}', r' ', p.strip())
        if not p: raise Exception('no phrase given')

        self.phrase = p

    def phraseIsCached(self):
        f = self.getCacheFile()
        return f.exists()

    def getCacheFile(self):
        return self.cacheDir / self.phrase

    def outputIsEmpty(self):
        return all(re.search(r'^\s*$', l) for l in self.outputLines)

    def loadCached(self):
        f = self.getCacheFile()
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

        if not self.dlAttempt: sys.stderr.write("no download\n")

    def processLines(self):
        self.outputLines = list(self.lines)

    def download(self):
        self.dlAttempt = True

        cmd = "timeout {tosec} lynx -dump".format(
            tosec = self.timeout_seconds,
        ).split()
        cmd += [self.phrase]

        pipe = Pipe(cmd)
        with self.getCacheFile().open('w') as fp:
            fp.write(pipe.stdout)
        self.lines = pipe.stdout.split("\n")
        
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
