set -eu
cd "$HOME/work/s1520"
set -a; . ./session.env; set +a
sed -i 's/time.sleep(35)/time.sleep(300)/' terminal-witness.py
python3 terminal-check.py xterm > a/terminal-check.log 2>&1
