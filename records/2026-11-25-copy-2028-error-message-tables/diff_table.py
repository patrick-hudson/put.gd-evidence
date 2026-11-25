#!/usr/bin/env python3
"""Before/after table of changed string literals: diff_table.py BASE HEAD paths..."""
import re,subprocess,sys
base,head=sys.argv[1:3];paths=sys.argv[3:]
diff=subprocess.run(['git','diff','-U0',f'{base}..{head}','--',*paths],capture_output=True,text=True).stdout
LIT=re.compile(r'"((?:[^"\\\n]|\\.)*)"')
rows=[];f=None;rem=[];add=[]
def flush():
    a=[x for x in rem if ' ' in x];b=[x for x in add if ' ' in x]
    sa=set(a);sb=set(b)
    a=[x for x in a if x not in sb];b=[x for x in b if x not in sa]
    for i in range(max(len(a),len(b))):
        rows.append((f,a[i] if i<len(a) else '',b[i] if i<len(b) else ''))
for l in diff.splitlines():
    if l.startswith('+++ '):flush();rem=[];add=[];f=l[6:];continue
    if l.startswith('@@'):flush();rem=[];add=[];continue
    if l.startswith('-') and not l.startswith('---'):rem+=LIT.findall(l[1:])
    elif l.startswith('+') and not l.startswith('+++'):add+=LIT.findall(l[1:])
flush()
e=lambda s:s.replace('|','\\|').replace('\\"','"')
print('| File | Before | After |\n|---|---|---|')
for f,a,b in rows:print(f'| `{f.split("/",1)[1]}` | {e(a)} | {e(b)} |')
print(f'\n{len(rows)} strings.',file=sys.stderr)
