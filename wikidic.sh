#!/bin/bash

set -u

urlBase="http://en.wiktionary.org/wiki"

if [ $# -lt 1 ]; then
	echo give a word >&2
	exit 1
fi

phrase="`echo $@`"
url="$urlBase/$phrase"

lynx -dump "$url" | less
