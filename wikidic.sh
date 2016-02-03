#!/bin/bash

set -u

urlBase="http://en.wiktionary.org/wiki"

if [ $# -lt 1 ]; then
	echo give a word >&2
	exit 1
fi

flgNoLess=0

arr=()
for a; do
	if [ $a = '-n' ]; then
		flgNoLess=1
		continue
	fi
	arr+=("$a")
done

phrase="`echo ${arr[@]}`"
url="$urlBase/$phrase"

if [ $flgNoLess -ne 0 ]; then
	lynx -dump "$url"
else
	lynx -dump "$url" | less
fi
