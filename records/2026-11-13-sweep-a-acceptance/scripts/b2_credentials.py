"""Read the authorized builder input only in memory; never print its values."""
import os,pathlib,re,stat

def block():
 p=pathlib.Path.home()/'Documents/creds.txt'; fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
 try:
  s=os.fstat(fd); assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600
  with os.fdopen(fd,'r') as f: text=f.read()
 except: os.close(fd); raise
 match=re.search('backblaze',text,re.I); assert match,'Backblaze-labelled block absent'
 value=text[match.start():]; next_block=re.search('cloudflare|amazon|proton|wasabi',value,re.I)
 return value[:next_block.start()] if next_block else value

def find(value,*labels):
 for label in labels:
  match=re.search(r'(?im)^\s*'+re.escape(label)+r'\s*:\s*(.+)$',value)
  if match: return match[1].strip()
 return None

def read():
 value=block(); key=find(value,'Access key ID','Application key ID','keyID','Key ID'); secret=find(value,'Secret access key','Application key','applicationKey','Secret key'); bucket=find(value,'Bucket name','Bucket','bucketName')
 assert key and secret,'Required Backblaze labelled fields absent'
 return key,secret,bucket

if __name__=='__main__':
 import json
 value=block(); labels=['Access key ID','Secret access key','Application key ID','Application key','keyID','Key ID','Secret key','Bucket name','Bucket','bucketName','Endpoint']
 print(json.dumps({label:find(value,label) is not None for label in labels}))
