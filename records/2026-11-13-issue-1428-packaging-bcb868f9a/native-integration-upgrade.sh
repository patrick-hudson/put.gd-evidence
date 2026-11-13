set -eu
out="$HOME/work/ocr-integration-bcb-artifacts"
package=$(find "$out/integration-ubuntu24.04" -maxdepth 1 -name '*.deb' -type f)
test -n "$package"
podman cp "$package" pg1438-native-size:/tmp/putgd-bcb.deb
podman exec -i pg1438-native-size sh > "$out/native-integration-upgrade.log" 2>&1 <<'UPGRADE'
set -eu
# Same development base version, different Git suffix: permit the lexical hash ordering.
apt-get install -y --allow-downgrades --no-install-recommends /tmp/putgd-bcb.deb
dpkg-query -W -f='${Package}\t${Version}\t${Installed-Size}\n' > /input/native-integration-installed.tsv
env -i /usr/bin/putgd-ocr --version-json > /input/native-integration-identity.json
dpkg-query -W -f='${Recommends}\n' putgd > /input/native-integration-recommends.txt
UPGRADE
python3 - <<'PY'
from pathlib import Path
import json,subprocess
r=Path.home()/'work/ocr-integration-bcb-artifacts'
a=Path.home()/'work/ocr-pkg-1438-artifacts'
def read(p):
 return {s[0]:(s[1],int(s[2])) for line in p.read_text().splitlines() if (s:=line.split('\t'))}
before=read(a/'native-head-baseline-installed.tsv');after=read(a/'native-integration-installed.tsv')
identity=json.loads((a/'native-integration-identity.json').read_text());assert identity['gitCommit']=='bcb868f9ac5b50967976656ed306858f5d8ae72f'
basepkg=next((a/'nightly-head-native').glob('*.deb'))
baserec=subprocess.check_output(['podman','exec','pg1438-native-size','dpkg-deb','-f','/input/nightly-head-native/'+basepkg.name,'Recommends'],text=True).strip()
assert baserec==(a/'native-integration-recommends.txt').read_text().strip()
changes=[{'package':name,'beforeKiB':before.get(name,('',0))[1],'afterKiB':after.get(name,('',0))[1],'version':after.get(name,('',0))[0]} for name in sorted(before.keys()|after.keys()) if before.get(name,('',0))[1]!=after.get(name,('',0))[1]]
d={'run':43380438975,'commit':identity['gitCommit'],'baselineRun':43355658846,'baselineCommit':'466449a4c69a07a1997668d1b70d637abac76a16','beforeKiB':sum(v[1] for v in before.values()),'afterKiB':sum(v[1] for v in after.values()),'addedKiB':sum(v[1] for v in after.values())-sum(v[1] for v in before.values()),'changes':changes,'recordingRecommendsUnchanged':True,'recommends':baserec,'identity':identity,'scope':'Exact integration CI DEB versus exact nightly-head installed baseline, package Installed-Size metadata; local artifacts, no signed-repository publication or desktop acceptance'}
(r/'native-integration-size.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
PY
