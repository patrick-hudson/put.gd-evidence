#!/bin/bash
set -eu
log=$1
out=$2
xterm -geometry 135x24+0+0 -fa Monospace -fs 12 -bg '#151515' -fg '#eeeeee' -e sh -c 'cat "$1"; sleep 20' sh "$log" &
term_pid=$!
trap 'kill -TERM "$term_pid" 2>/dev/null || true; wait "$term_pid" 2>/dev/null || true' EXIT
sleep 1
import -window root -trim "$out"
