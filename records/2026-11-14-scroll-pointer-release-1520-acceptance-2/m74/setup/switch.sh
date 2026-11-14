set -eu
cd "$HOME/work/s5202"
. ./session.env
from=$1
to=$2
bin/cli-$from ui.quit > "$from/quit-before-switch-$(date -u +%H%M%S).json"
sleep 1
sudo -n apt-get --no-install-recommends install -y "$HOME/work/s5202/after.deb" >install-candidate.log 2>&1
sh start.sh "$to"
