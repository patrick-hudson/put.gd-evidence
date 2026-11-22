#!/bin/bash
set -eu
host=$1; shift
case $host in m74) ip=74;; k72) ip=72;; *) exit 2;; esac
options=(-i /home/patrick/.ssh/awskey_110724 -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes -o UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/"$host"/known_hosts)
case $1 in
put) shift; scp "${options[@]}" "$1" "patrick@192.168.68.$ip:$2" ;;
get) shift; scp -rp "${options[@]}" "patrick@192.168.68.$ip:$1" "$2" ;;
*) ssh -n "${options[@]}" "patrick@192.168.68.$ip" "$@" ;;
esac
