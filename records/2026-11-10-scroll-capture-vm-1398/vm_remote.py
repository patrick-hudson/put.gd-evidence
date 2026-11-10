import subprocess,sys
BASE='/home/patrick/work/svm1398/repo'
SSH=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts','patrick@192.168.68.69']
def remote(s,**kw):return subprocess.run(SSH+[s],check=True,**kw)
if __name__=='__main__':remote(sys.argv[1])
