#!/bin/bash
# resident.sh start|stop|cli ... : this build's put.gd resident with its own config, data and cache, the helper's debug log on.
lab=$HOME/work/scroll-session/gnome
set -a; . "$lab/session.env"; set +a
export XDG_CONFIG_HOME=$lab/res/config XDG_DATA_HOME=$lab/res/data XDG_CACHE_HOME=$lab/res/cache PUTGD_RECORD_DEBUG_LOG=$lab/res/helper.log
bin=$lab/../repo/build/dev
case $1 in
start)
    mkdir -p "$lab/res/config" "$lab/res/data" "$lab/res/cache" "$lab/res/out"
    setsid nohup "$bin/putgd" > "$lab/res/resident.log" 2>&1 < /dev/null &
    echo $! > "$lab/res/resident.pid"; echo "started $(cat $lab/res/resident.pid)";;
stop)
    pid=$(cat "$lab/res/resident.pid"); c=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null)
    case "$c" in *build/dev/putgd*) kill "$pid"; echo "stopped $pid";; *) echo "not running: $c";; esac;;
cli)
    shift; exec "$bin/putgd-cli" "$@";;
esac
