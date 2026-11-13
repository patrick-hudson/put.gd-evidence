#!/bin/sh
# guest_run.sh RUN SSH_PORT DESKTOP LEADER WIDTH HEIGHT X1 Y1 X2 Y2 [extra text_proof.py arguments]
# Runs text_proof.py inside a lab guest from its QEMU host. The guest's pointer
# and keys come from the VM's own QMP socket, forwarded into the guest for the
# length of the run, so the compositor sees a tablet and a keyboard.
set -eu
run=$1; port=$2; desktop=$3; leader=$4; w=$5; h=$6; x1=$7; y1=$8; x2=$9; shift 9; y2=$1; shift
root=$HOME/work/t1428d; R=$root/work/lab-runs/$run
G="-i $R/identity -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=$R/known_hosts -o ConnectTimeout=10 -o ServerAliveInterval=20 -p $port"
scp -q -P "$port" -i "$R/identity" -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$R/known_hosts" \
  "$root/proof/text_proof.py" "$root/proof/fake-putgd-ocr.py" lab@127.0.0.1:tp/
ssh $G lab@127.0.0.1 'cd ~/tp && rm -f qmp.sock click.txt && install -m 0755 fake-putgd-ocr.py squashfs-root/usr/bin/putgd-ocr'
A=/home/lab/tp/squashfs-root
exec ssh $G -o ExitOnForwardFailure=yes -R /home/lab/tp/qmp.sock:"$R/qmp.sock" lab@127.0.0.1 \
  "cd ~/tp && python3 text_proof.py --desktop '$desktop' --leader $leader --app $A/AppRun \
   --cli 'env LD_LIBRARY_PATH=$A/usr/lib:$A/usr/lib/putgd $A/usr/bin/putgd-cli' --input-socket /home/lab/tp/qmp.sock \
   --screen $w $h --region $x1 $y1 $x2 $y2 --ask-click /home/lab/tp/click.txt --rfb none --real-profile $*"
