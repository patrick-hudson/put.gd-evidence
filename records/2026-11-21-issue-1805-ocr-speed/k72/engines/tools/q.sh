# q.sh RUNNER IMAGE ARGS... : one capture, print CER/WER vs truth and timing fields
cd ~/work/r1805; mkdir -p engines/scratch
R=$1; I=$2; shift 2
engines/rapidocr/venv/bin/python -I engines/tools/$R $I "$@" 2>/dev/null | tail -1 > engines/scratch/q.json
python3 -I -c "
import json,sys; sys.path.insert(0,'engines/tools'); from bench2 import rates
d=json.load(open('engines/scratch/q.json')); t=open(sys.argv[1].rsplit('.',1)[0]+'.txt').read()
c,w=rates(t,d.pop('text')); print('CER %.4f WER %.4f' % (c,w), d)" $I
