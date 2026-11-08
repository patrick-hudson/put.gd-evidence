export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=$(ls /run/user/1000 | grep '^wayland-[0-9]*$' | head -1)
foot -a win1 -T win1 -W 60x20 sh -c "while :; do date +%s.%N; sleep 0.05; done" > /dev/null 2>&1 & F=$!
sleep 3
if [ "$RECONNECT" = 1 ]; then for i in $(seq 1 $N); do ~/mg/mincap win1 1 $SECS 0; sleep 0.5; done; else ~/mg/mincap win1 $N $SECS 500; fi | cut -d" " -f3-
kill $F
