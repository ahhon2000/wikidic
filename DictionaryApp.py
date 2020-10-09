import os, sys
import argparse
import pydoc
import re

from EasyPipe import Pipe

DFLT_TIMEOUT_SECONDS = 25

class _Address:
    def __init__(self, addr):
        self.regex = None
        self.lineNum = None
        self.isLineNum = isinstance(addr, int)

        if self.isLineNum:
            self.lineNum = addr
        else:
            self.regex = re.compile(r'' + addr)

    def chkMatch(self, i, l):
        if self.isLineNum:
            if i == self.lineNum: return True
        else:
            if self.regex.search(l): return True

        return False


def _delCopyLines(ls, *addrs, mode=None):
    if len(addrs) not in (1, 2): raise Exception('wrong # of args')
    if mode not in ('copy', 'delete'): raise Exception('unsupported mode')

    addr1 = addrs[0]
    addr2 = addrs[0] if len(addrs) == 1 else addrs[1]
    if addr2 is None: addr2 = len(ls) - 1

    (addr1, addr2) = map(_Address, (addr1, addr2))

    ols = []
    flgInside = False
    for i, l in enumerate(ls):
        flgAddr1Matched = False
        if not flgInside:
            if addr1.chkMatch(i, l):
                flgInside = True
                flgAddr1Matched = True

        if any((
            mode == 'copy' and flgInside,
            mode == 'delete' and not flgInside
        )):
            ols += [l]

        if len(addrs) == 1:
            flgInside = False
        elif flgInside and not flgAddr1Matched  or  addr2.isLineNum:
            if addr2.chkMatch(i, l):
                flgInside = False

    return ols

def delLines(ls, *addrs):
    """Return a copy of ls with certain lines removed

    USAGE: delLines(ls, ADDR1, ADDR2)
    USAGE: delLines(ls, ADDR1)
    
    Addresses can be either line numbers (starting with 0) or regexps.
    If ADDR2 is None then delete until the last line, incl.
    With only one address (ADDR1), remove lines matching ADDR1. Otherwise,
    remove lines from ADDR1 to ADDR2, incl.
    """

    return _delCopyLines(ls, *addrs, mode='delete')

def copyLines(ls, *addrs):
    """Return a copy of ls that contains only lines matching the addresses

    USAGE: copyLines(ls, ADDR1, ADDR2)
    USAGE: copyLines(ls, ADDR1)
    
    Addresses can be either line numbers (starting with 0) or regexps.
    If ADDR2 is None then copy until the last line, incl.
    With only one address (ADDR1), copy lines matching ADDR1. Otherwise,
    copy lines from ADDR1 to ADDR2, incl.
    """
    return _delCopyLines(ls, *addrs, mode='copy')


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
            self.lines = list(re.sub(r'\n$', r'', l) for l in fp)

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
