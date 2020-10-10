import os
import re
from pathlib import Path

from DictionaryApp import DictionaryApp, delLines, copyLines

def _codicPostprocess(ls):
    ols = []
    ts = []  # transcriptions
    for l in ls:
        flgTr = False
        if re.search(r'^\s*[(][^)(]+[)]\s*$', l):
            if not re.search(r'[0-9]', l):
                flgTr = True
        elif re.search(r'[(][^)(]+[)]', l):
            s = re.sub(r'.*[(]([^)(]+)[)].*', r'\1', l)
            for c in "'ˌʒʃðθæɛəɑɔʊ:":
                if c in s:
                    flgTr = True
                    break

        if flgTr: ts += [l]

    for t in ts: ols += [t]
    if ts: ols += ["     *"]

    ols += ls

    return ols

class DictionaryAppCO(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.collinsdictionary.com/dictionary/english"
        self.cacheDir = Path(os.environ.get('HOME')) / '.codic_cache'

    def processLines(self):
        ols = self.lines

        for flt in (
            lambda ls: delLines(ls, 0, r'^Definition\s+of\s+' + "'"),
            lambda ls: delLines(ls, r'^[()*\s]+$'),
            lambda ls: delLines(ls, r'^\s*Word Frequency\s*$'),
            lambda ls: delLines(ls, r'^Translations for\b', None),
            lambda ls: delLines(ls, r'^Trends of\b', None),
            lambda ls: delLines(ls, r'^\s*References\s*$', None),
            lambda ls: delLines(ls, r'^\s*Share\s*$', None),
            _codicPostprocess,
        ):
            ols = flt(ols)

        self.outputLines = list(ols)
