#!/bin/sh
# Builds the prototype tests. Usage: ./build.sh [asan]
set -e
cd "$(dirname "$0")"
SRCS="scroll_stitcher.cpp scroll_session.cpp synthetic_app.cpp test_main.cpp"
FLAGS="-std=c++20 -O2 -Wall -Wextra"
if [ "$1" = "asan" ]; then
  nice -n 19 g++ $FLAGS -g -fsanitize=address,undefined -fno-omit-frame-pointer $SRCS -o test_stitcher_asan
else
  nice -n 19 g++ $FLAGS $SRCS -o test_stitcher
fi
