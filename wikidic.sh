#!/bin/bash

set -u

urlBase="http://en.wiktionary.org/wiki"
pager="cat"
dirCache="/tmp/.wikidic_cache"

rmScum() {
	sed '/^Contents\>/,/^[^[:space:]]/d; /^Translation/,/^[^[:space:]]/d; /^Navigation menu/,$d; /^Anagrams/,/^[^[:space:]]/d; /^Statistics/,/^[^[:space:]]/d; /^Related terms/,/^[^[:space:]]/d; /^Derived terms/,/^[^[:space:]]/d;'
	
}


if [ $# -lt 1 ]; then
	echo give a word >&2
	exit 1
fi

mkdir -p "$dirCache"

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

if [ $flgNoLess -eq 0 ]; then
	pager=less
fi

fileCache="$dirCache/$phrase"
if [ '!' -e "$fileCache" ]; then
	lynx -dump "$url" > "$fileCache"
fi

cat "$fileCache" | rmScum | "$pager"
