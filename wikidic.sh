#!/bin/bash
#
# USAGE: wikidic WORD

set -u

urlBase="http://en.wiktionary.org/wiki"
pager="cat"
dirCache="$HOME/.wikidic_cache"

dlAttempt=0

rmScum() {
    sed '/^Contents\>/,/^[^[:space:]]/d; /^Translation/,/^[^[:space:]]/d; /^Navigation menu/,$d; /^Anagrams/,/^[^[:space:]]/d; /^Statistics/,/^[^[:space:]]/d; /^Related terms/,/^[^[:space:]]/d; /^Derived terms/,/^[^[:space:]]/d;'
    
}

outputter() {
    cat "$fileCache" | rmScum | "$pager"
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
    dlAttempt=1
    lynx -dump "$url" > "$fileCache"
fi

outputter
if [ "$dlAttempt" -eq 0 ]; then
    echo 'no download' >&2
fi
