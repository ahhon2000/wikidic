#!/bin/bash
#
# USAGE: wikidic WORD
#	 or:
#	 wikidic -c   # clear cache

set -u

urlBase="http://en.wiktionary.org/wiki"
pager="cat"
dirCache="$HOME/.wikidic_cache"

rmScum() {
	sed '/^Contents\>/,/^[^[:space:]]/d; /^Translation/,/^[^[:space:]]/d; /^Navigation menu/,$d; /^Anagrams/,/^[^[:space:]]/d; /^Statistics/,/^[^[:space:]]/d; /^Related terms/,/^[^[:space:]]/d; /^Derived terms/,/^[^[:space:]]/d;'
	
}

if [ $# -eq 1 ] && [ "$1" = '-c' ]; then
	# clear cache
	find "$dirCache" -mindepth 1 -maxdepth 1 -delete
	exit 0
fi

if [ $# -lt 1 ]; then
	echo give a word >&2
	exit 1
fi

mkdir -p "$dirCache"

flgNoLess=0

arr=()
for a; do
	if [ "$a" = '-n' ]; then
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
