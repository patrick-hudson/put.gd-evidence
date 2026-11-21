#!/bin/bash
# usage: shape.sh on RATE_KBIT MINUTES NET... | off | show
# Limits only HTTPS uploads from eno1 to the given Backblaze networks; a watchdog removes it.
set -e
dev=eno1
here=$(dirname "$(readlink -f "$0")")
if [ "$1" = off ]; then
  [ -f "$here/watchdog.pid" ] && kill "$(cat "$here/watchdog.pid")" 2>/dev/null || true
  rm -f "$here/watchdog.pid"
  sudo -n tc qdisc del dev $dev root 2>/dev/null || true
  tc qdisc show dev $dev; exit 0
fi
if [ "$1" = show ]; then tc -s class show dev $dev; tc filter show dev $dev; exit 0; fi
rate=$2; minutes=$3; shift 3
[ -f "$here/watchdog.pid" ] && kill "$(cat "$here/watchdog.pid")" 2>/dev/null || true
sudo -n tc qdisc replace dev $dev root handle 1: htb default 10
sudo -n tc class add dev $dev parent 1: classid 1:10 htb rate 10gbit
sudo -n tc qdisc add dev $dev parent 1:10 fq_codel
sudo -n tc class add dev $dev parent 1: classid 1:20 htb rate ${rate}kbit ceil ${rate}kbit
sudo -n tc qdisc add dev $dev parent 1:20 fq_codel
for net in "$@"; do
  sudo -n tc filter add dev $dev parent 1: protocol ip prio 5 u32 match ip dst $net match ip dport 443 0xffff flowid 1:20
done
setsid bash -c "sleep $((minutes*60)); sudo -n tc qdisc del dev $dev root 2>/dev/null" < /dev/null > /dev/null 2>&1 &
echo $! > "$here/watchdog.pid"
tc -s class show dev $dev | head -8
