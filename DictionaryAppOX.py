import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp, delLines, copyLines


def _rmScum(ls):
    ret = []
    flgScum = True
    for l in ls:
        if re.search(
            r'(meaning|definition).*\s+of.*in', l,
            flags=re.IGNORECASE,
        ):
            flgScum = False

        if re.search(
            '^\s*[^\s]*\s*Word of the Day\s*$', l,
            flags=re.IGNORECASE,
        ):
            flgScum = True

        if flgScum: continue
        if re.search('^\s*Translate\s.*into\s[A-Z][^\s]+\s*$', l): continue

        ret += [l]

    return ret

def _transcr(ls):
    ret = []
    ts = []  # transcriptions
    for l in ls:
        trConds = [re.search(r'[/][^/]+[/]', l)]
        trConds += list(l.find(s) < 0 for s in ('http', 'www.'))
        if all(trConds): ts += [l]

    ret += ["     *"] if ts else []
    ret += ts
    for l in ls: ret += [l]

    return ret

class DictionaryAppOX(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.lexico.com/definition"
        self.cacheDir = Path(os.environ.get('HOME')) / '.oxdic_cache'

    def processLines(self):
        ols = self.lines

        for flt in (
            _rmScum,
            _transcr,
        ):
            ols = flt(ols)

        self.outputLines = ols
