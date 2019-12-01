#!/bin/bash
#
# USAGE: wikidic WORD
#	 or:
#	 wikidic -c   # clear cache

set -u

#urlBase="http://en.oxforddictionaries.com/definition"
urlBase="http://www.lexico.com/en/definition"
pager="cat"
dirCache="$HOME/.oxdic_cache"
TIMEOUT_SECONDS=25
pathScript="`readlink -f "$0"`"
dirScript="`dirname "$pathScript"`"
preprocess="$dirScript/oxdicPreprocess"
fileTmp="/tmp/.oxdicCache.$$.$RANDOM"

rmScum() {
	sed -n '/definition.*\s\+of.*in/I,/^\s\+Word of the Day/p;'
}


print_usage(){
	fd=1
	[ "$1" -ne 0 ] && fd=2
	cat >&$fd << EOF
Usage: $0 [options]...
    -h, --help               Print help
    -r, --redownload         Redownload article if empty
EOF
	exit "$1"
}

outputter() {
	cat "$fileCache" | rmScum | "$preprocess" | "$pager"
}


SHORTOPTS='hnr'
LONGOPTS='help,no-less,redownload'
args=`getopt -l $LONGOPTS $SHORTOPTS "$@"` || print_usage 1 >&2

eval set -- $args

flgNoLess=0
flgRedownload=0

while [ "$1" '!=' -- ]; do
	case "$1" in
		--help | -h)
			print_usage 0 >&1
		;;
		--no-less | -n)
			flgNoLess=1
		;;
		--redownload | -r)
			flgRedownload=1
		;;
		?)
			print_usage 1
		;;
	esac
	shift
done
shift


if [ $# -lt 1 ]; then
	echo give a word >&2
	exit 1
fi

mkdir -p "$dirCache"

arr=()
for a; do
	arr+=("$a")
done

phrase="`echo ${arr[@]}`"
url="$urlBase/$phrase"

if [ $flgNoLess -eq 0 ]; then
	pager=less
fi

fileCache="$dirCache/$phrase"
if [ '!' -e "$fileCache" ] || ( [ $flgRedownload -ne 0 ] && ! outputter | grep '[^[:space:]]'  > /dev/null ); then
#	rm -f "$fileTmp"
#	wget --max-redirect 100 --timeout "$TIMEOUT_SECONDS" --quiet "$url" -O "$fileTmp"
#	wget --max-redirect 100 --timeout "$TIMEOUT_SECONDS" "$url" -O "$fileTmp"
	timeout $TIMEOUT_SECONDS lynx -dump "$url" > "$fileCache"
#	rm -f "$fileTmp"
fi

outputter
