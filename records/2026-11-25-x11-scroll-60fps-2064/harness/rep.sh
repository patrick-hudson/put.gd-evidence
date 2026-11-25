# rep.sh TAG DRIVER HELPER: brisk you-scroll repeats, no references
cd ~/work/x2064/lab || exit 1
export LAB_X11=1 LAB_DRIVER=$2 LAB_HELPER=$3 LAB_NOREF=1 LAB_PACE=brisk
B=$1; rm -f rep-$B.done
{ for seed in 4 5 6; do LAB_SEED=$seed LAB_TAG=$B-b$seed python3 run.py firefox github,stackoverflow user; done; } > rep-$B.log 2>&1
echo DONE > rep-$B.done
