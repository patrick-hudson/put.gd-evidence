# observe.sh OUTFILE CMD... : run CMD, sample its fds, exec mappings, children and ~/.cache writes
O=$1; shift
touch ~/work/r1805/engines/scratch/marker
"$@" > /dev/null 2> $O.err &
P=$!
: > $O.fds; : > $O.maps; : > $O.kids
while kill -0 $P 2>/dev/null; do
  ls -l /proc/$P/fd 2>/dev/null | awk '{print $NF}' >> $O.fds
  awk '$2 ~ /x/ {print $2, $6}' /proc/$P/maps 2>/dev/null >> $O.maps
  for t in /proc/$P/task/*/children; do cat $t 2>/dev/null; done >> $O.kids
  sleep 0.05
done
wait $P; echo "exit $?" > $O.exit
echo "== fds (unique, non-pipe)"; sort -u $O.fds | grep -v "pipe:\|^$\|total" | sed 's/[0-9]\+\]$/N]/' | sort -u
echo "== exec mappings without a file (anon/JIT)"; grep -v " /" $O.maps | sort | uniq -c
echo "== exec-mapped files"; awk '{print $2}' $O.maps | grep "^/" | sort -u | sed 's|.*/||' | tr '\n' ' '; echo
echo "== child pids seen: $(tr ' ' '\n' < $O.kids | grep -c .)"
echo "== files written under ~/.cache, /tmp, cwd since start:"; find ~/.cache /tmp/ ~/work/r1805 -newer ~/work/r1805/engines/scratch/marker -type f 2>/dev/null | grep -v "engines/scratch/obs\|runs/" | head
cat $O.exit
