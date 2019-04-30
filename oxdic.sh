#!/bin/bash
#
# USAGE: wikidic WORD
#	 or:
#	 wikidic -c   # clear cache

set -u

urlBase="https://en.oxforddictionaries.com/definition"
pager="cat"
dirCache="$HOME/.oxdic_cache"
TIMEOUT_SECONDS=25
pathScript="`readlink -f "$0"`"
dirScript="`dirname "$pathScript"`"
preprocess="$dirScript/oxdicPreprocess"

rmScum() {
	sed -n '/definition.*\s\+of.*in/I,/^\s\+Word of the Day/p;'
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
	timeout "$TIMEOUT_SECONDS" lynx -dump "$url" > "$fileCache"
fi

cat "$fileCache" | rmScum | "$preprocess" | "$pager"
