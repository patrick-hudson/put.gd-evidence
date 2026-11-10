#!/bin/bash
set -u
root=/var/home/patrick/a1364
name=$1; shift
python3 "$root/lab/record_run.py" --run "$root/runs/$name" --build "pr=$root/pr.AppImage" --analyzer "$root/analyzer/squashfs-root" --video marker --rounds 1 --no-notifications --keep-unpaired --real-data-home --frames "$@" > "$root/runs/$name.out" 2>&1
rc=$?
printf 'case %s rc=%s\n' "$name" "$rc"
python3 "$root/lab/summarize_run.py" "$root/runs/$name/results.json"
pactl get-default-source
pactl get-default-sink
pactl list short sources
pactl list short modules | grep putgd_lab || true
