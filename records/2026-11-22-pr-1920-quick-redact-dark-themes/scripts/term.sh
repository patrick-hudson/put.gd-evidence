#!/bin/bash
if [ "$#" -eq 3 ]; then
    printf '\033]11;#%s\007\033]10;#%s\007' "$2" "$3"
fi
printf '\033[2J\033[H\033[?25l'
cat -- "$1"
sleep infinity
