#!/bin/bash
# usage: stall.sh on API_IP NET... | off
# On top of shape.sh: drop every packet to the upload networks except the API address,
# so upload connections stall while put.gd can still list versions.
dev=eno1
if [ "$1" = off ]; then
  sudo -n tc filter del dev $dev parent 1: prio 2 2>/dev/null
  sudo -n tc filter del dev $dev parent 1: prio 3 2>/dev/null
  tc filter show dev $dev | grep -c "prio [23]" ; exit 0
fi
api=$2; shift 2
sudo -n tc filter add dev $dev parent 1: protocol ip prio 2 u32 match ip dst $api/32 flowid 1:20
for net in "$@"; do
  sudo -n tc filter add dev $dev parent 1: protocol ip prio 3 u32 match ip dst $net action drop
done
tc filter show dev $dev | grep -c "prio 3"
