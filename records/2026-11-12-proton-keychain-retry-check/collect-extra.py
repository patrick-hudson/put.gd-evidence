import subprocess as s,pathlib,re,json
b=pathlib.Path('/tmp/kr19');out=b/'2026-11-12-proton-keychain-retry-check'
for host,ip in [('k72','72'),('d69','69')]:
 ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o',f'UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/{host}/known_hosts',f'patrick@192.168.68.{ip}']
 for path in re.findall(r'receipt on the host: (\S+)',(out/(host+'-leases.log')).read_text()):
  (out/(host+'-'+pathlib.Path(path).name)).write_bytes(s.check_output(ssh+['cat '+path]))
 (out/(host+'-environment-corrected.txt')).write_bytes(s.check_output(ssh+['cat /etc/os-release; dpkg-query -W plasma-workspace kwin-wayland; uname -r']))
