# batch.sh TAG DRIVER HELPER
cd ~/work/x2064/lab || exit 1
export LAB_X11=1 LAB_DRIVER=$2 LAB_HELPER=$3
B=$1
rm -f batch-$B.done
{
for seed in 1 2; do LAB_SEED=$seed LAB_TAG=$B-s$seed python3 run.py firefox github,stackoverflow,wiki user; done
LAB_PACE=brisk LAB_SEED=3 LAB_TAG=$B-brisk python3 run.py firefox github,stackoverflow user
LAB_TAG=$B python3 run.py firefox github,wiki auto
} > batch-$B.log 2>&1
echo DONE > batch-$B.done
