import os
import re
from pathlib import Path
import calendar

from DictionaryApp import DictionaryApp, delLines, copyLines

class DictionaryAppMW(DictionaryApp):
    def __init__(self, *arg, **kwarg):
        DictionaryApp.__init__(self, *arg, **kwarg)

        self.urlBase = "https://www.merriam-webster.com/dictionary"
        self.cacheDir = Path(os.environ.get('HOME')) / '.mwdic_cache'

    def processLines(self):
        ols = self.lines

        emptyMarkers = re.compile(r"^\s*The word you've entered isn't in the dictionary")
        flgEmpty = False
        def detectEmptyArticle(ls):
            nonlocal emptyMarkers, flgEmpty
            for l in ls:
                if emptyMarkers.search(l):
                    flgEmpty = True
                    break
                yield l

        def fmtExampleLine(l):
            indentRe = re.compile(r'^(?P<indent>\s*)(?P<content>.*)')
            indentDic = {
                    'indent': indentRe.sub(r'\g<indent>', l),
                    'indent2': indentRe.sub(r'\g<indent>', l) * 2,
            }
            poss = ('noun', 'adjective', 'verb', 'adverb', 'preposition',
                'pronoun', 'conjunction', 'exclamation', 'interjection',
            )
            posRe = re.compile(r'\s*\b(?P<pos>{poss})\b\s*'.format(
                    poss = "|".join(pos.capitalize() for pos in poss)
                ),
                flags=re.MULTILINE,
            )
            subSecRe = re.compile(
                r'\s*(?P<section>{sections})\s*'.format(
                    sections = "|".join((
                        'Examples on the Web:',
                        'Recent Examples on the Web:',
                    )),
                ),
                flags=re.MULTILINE,
            )
            exDelimRe = re.compile(
                r'\s+—\s+\[\d+\]',
                flags=re.MULTILINE,
            )
            quoteDateRe = re.compile(
                r'\s*\b(?P<date>\d{{1,2}}\s+({months})[.]?\s+\d{{4}})\b\s*'.format(
                    months = "|".join(
                        calendar.month_abbr[m+1] for m in range(12)
                    ),
                ),
                flags = re.MULTILINE,
            )

            l = posRe.sub(r'\n\g<pos>\n',l)
            l = subSecRe.sub(
                r'\n\g<section>\n', l,
            )

            l = exDelimRe.sub(r'\n-- from:\n', l)
            l = quoteDateRe.sub(r'\n\g<date>\n--------\n', l)

            ls = l.split("\n")
            for flt in (
                lambda ll: re.sub(r'^\s*', r'{indent2}'.format(**indentDic),ll),
                lambda ll: subSecRe.sub(
                    r'{indent}\g<section>'.format(**indentDic),
                    ll,
                ),
                lambda ll: posRe.sub(
                    r'{indent}\g<pos>'.format(**indentDic),
                    ll,
                ),
            ):
                for i, ll in enumerate(ls):
                    ls[i] = flt(ll)

            l = "\n".join(ls)

            return l

        def fmtExamples(ls):
            flgExSection = False
            exSectionStart = re.compile(
                r'^Examples of\b.*\bin a Sentence',
                flags=re.IGNORECASE,
            )
            exSectionEnd = re.compile(r'^[^\s]')
            for l in ls:
                if flgExSection:
                    if exSectionEnd.search(l):
                        flgExSection = False
                    else:
                        l = fmtExampleLine(l)
                if exSectionStart.search(l): flgExSection = True
                yield l
        
        for flt in (
            lambda ls: detectEmptyArticle(ls),
            lambda ls: copyLines(ls, r'^[^\s]', None),
            lambda ls: delLines(ls, r'^\s*Dictionary Entries near', None),
            lambda ls: delLines(ls, r'^\s*\[[0-9]*\]Save\s+Word\s*$'),
            lambda ls: delLines(ls, r'^\s*Log In\s*$'),
            lambda ls: delLines(ls, r'^\s*To save this word, you.ll need to log in'),
            lambda ls: delLines(ls, r'^\s*SAVED WORDS.*\bview recents\b\s*$'),
            lambda ls: delLines(ls, r'^\s*References\s*$', None),
            fmtExamples,
        ):
            ols = flt(ols)

        ols = list(ols)
        self.outputLines = [] if flgEmpty else ols
