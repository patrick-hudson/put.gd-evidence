#!/bin/bash
cd ~/work/b1792/h
python3 run.py final configure > final-config.log 2>&1
python3 run.py final upload large200 2 200 > final-large200.log 2>&1
./chain.sh final
