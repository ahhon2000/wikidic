import os, sys
import argparse
import re

DFLT_TIMEOUT_SECONDS = 25

class _AddressBase:
    def __init__(self):
        self.regex = None
        self.lineNum = None
        self.isLineNum = False

    def chkMatch(self, i, l):
        return False

class _AddressInt(_AddressBase):
    def __init__(self, addr):
        _AddressBase.__init__(self)
        self.lineNum = addr
        self.isLineNum = True

    def chkMatch(self, i, l):
        return i == self.lineNum

class _AddressRe(_AddressBase):
    def __init__(self, addr):
        _AddressBase.__init__(self)
        self.regex = re.compile(r'' + addr)
        self.isLineNum = False

    def chkMatch(self, i, l):
        return self.regex.search(l)

class _AddressLastLine(_AddressBase):
    def __init__(self):
        _AddressBase.__init__(self)


def _Address(addr):
    if isinstance(addr, int): return _AddressInt(addr)
    elif addr is None: return _AddressLastLine()
    return _AddressRe(addr)


def _delCopyLines(ls, *addrs, mode=None):
    if len(addrs) not in (1, 2): raise Exception('wrong # of args')
    if mode not in ('copy', 'delete'): raise Exception('unsupported mode')

    addr1 = addrs[0]
    addr2 = addrs[0] if len(addrs) == 1 else addrs[1]

    (addr1, addr2) = map(_Address, (addr1, addr2))

    flgInside = False
    for i, l in enumerate(ls):
        flgAddr1Matched = False
        if not flgInside:
            if addr1.chkMatch(i, l):
                flgInside = True
                flgAddr1Matched = True

        if not flgInside and mode == 'delete' or \
            flgInside and mode == 'copy':

            yield l

        if len(addrs) == 1:
            flgInside = False
        elif flgInside and not flgAddr1Matched  or  addr2.isLineNum:
            if addr2.chkMatch(i, l):
                flgInside = False

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
        self.result = None

        self.timeout_seconds = DFLT_TIMEOUT_SECONDS

        self._parseCLArgs()

    def _parseCLArgs(self):
        argp = argparse.ArgumentParser()

        argp.add_argument('-j', '--json', action="store_true", help="JSON output")
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
        strEmpt = re.compile(r'^\s*$')
        for l in self.outputLines:
            if not strEmpt.search(l): return False
        return True

    def loadCached(self):
        f = self.getCacheFile()
        with f.open() as fp:
            self.lines = list(l.rstrip("\n") for l in fp)

    def output(self):
        out = None
        if self.options.json:
            import json
            out = json.dumps(self.result) + "\n"
        else:
            out = self.result['text'] + "\n"

        if not self.pager or self.options.no_less:
            # without a pager
            sys.stdout.write(out)
        else:
            # with a pager
            import pydoc
            oldpager = os.environ.get('PAGER', '')
            pydoc.pager(out)
            os.environ['PAGER'] = oldpager

    def processLines(self):
        self.outputLines = list(self.lines)

    def download(self):
        self.dlAttempt = True

        cmd = "timeout {tosec} lynx -dump".format(
            tosec = self.timeout_seconds,
        ).split()
        cmd += [self.urlBase + '/' + self.phrase]

        from EasyPipe import Pipe
        pipe = Pipe(cmd)
        with self.getCacheFile().open('w') as fp:
            fp.write(pipe.stdout)
        self.lines = pipe.stdout.split("\n")
        
    def run(self, output=True):
        flgCached = self.phraseIsCached()
        if flgCached:
            self.loadCached()
            self.processLines()

        if not flgCached  or  \
            self.outputIsEmpty() and self.options.redownload:

            self.download()
            self.processLines()

        self.result = {
            'text': "\n".join(self.outputLines),
            'emsg': '',
            'status': 0,
            'dlAttempt': self.dlAttempt,
        }

        if output: self.output()

        return self.result
