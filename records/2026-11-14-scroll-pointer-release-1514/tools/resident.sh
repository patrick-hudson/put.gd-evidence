#!/bin/sh
# resident.sh start LABEL BIN | stop LABEL | cli LABEL METHOD JSON
# A put.gd resident of one build with its own config, data and cache under
# ~/work/scroll-1514-lab/LABEL, in the desktop session, with the helper's
# debug log. Local save only: archive.keepUploads, no destination.
set -eu
lab=$HOME/work/scroll-1514-lab
set -a
. "$lab/session.env"
set +a
cmd=$1
label=$2
dir=$lab/$label
export XDG_CONFIG_HOME=$dir/config XDG_DATA_HOME=$dir/data XDG_CACHE_HOME=$dir/cache
export PUTGD_RECORD_DEBUG_LOG=$dir/helper.log
case $cmd in
start)
    bin=$3
    mkdir -p "$dir/config" "$dir/data" "$dir/cache"
    setsid nohup "$bin" > "$dir/resident.log" 2>&1 < /dev/null &
    echo $! > "$dir/resident.pid"
    echo "started $(cat "$dir/resident.pid")"
    ;;
stop)
    pid=$(cat "$dir/resident.pid")
    kill "$pid" 2>/dev/null || :
    echo "stopped $pid"
    ;;
cli)
    shift 2
    exec "$CLI" "$@"
    ;;
esac
