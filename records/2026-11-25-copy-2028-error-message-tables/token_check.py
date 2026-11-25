#!/usr/bin/env python3
"""Per-hunk fact check for #2028 copy PRs: every fact token in a removed string literal must still
appear in the hunk's added string literals. Run from the repo root: token_check.py BASE HEAD [paths...]
Tokens: failure codes (snake_case), %N and {name} placeholders, IAM permissions, paths, URLs, numbers
with units, `code`, HTTP statuses. Prints one line per loss and a summary; exit 1 on any loss."""
import re,subprocess,sys,collections
base,head=sys.argv[1:3];paths=sys.argv[3:] or ['src']
diff=subprocess.run(['git','diff','-U0',f'{base}..{head}','--',*paths],capture_output=True,text=True).stdout
LIT=re.compile(r'"((?:[^"\\\n]|\\.)*)"')
TOK=[('placeholder',r'%\d+|\{[A-Za-z_:%0-9]+\}'),('iam',r'\b[a-z0-9]+:[A-Z][A-Za-z*]+\b'),('code',r'\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b'),
     ('url',r'https?://[^\s"]*|\b[a-z0-9.-]+\.(?:put\.gd|com|org)\b'),('path',r'(?:~|\$[A-Z_]+|\.\.?)?/[\w./+-]*[\w+-]'),
     ('number',r'\b\d+(?:\.\d+)?\s?(?:KB|MB|GB|TB|KiB|MiB|GiB|ms|s|seconds?|minutes?|hours?|days?|px|%)?(?=\W|$)'),('backtick',r'`[^`]+`'),
     ('http',r'\bHTTP \d{3}\b')]
def toks(s):
    out=collections.Counter()
    for kind,rx in TOK:
        for m in re.findall(rx,s):out[(kind,m.strip())]+=1
    return out
files=0;hunks=0;losses=[]
cur=None
def flush(f,line,rem,add):
    global hunks
    if not rem:return
    a=toks(' '.join(rem));b=toks(' '.join(add));hunks+=1
    for k,n in a.items():
        if b[k]<n and k[1] not in ' '.join(add):losses.append((f,line,k,n-b[k]))
f=None;line=0;rem=[];add=[]
for l in diff.splitlines():
    if l.startswith('+++ '):flush(f,line,rem,add);rem=[];add=[];f=l[6:];files+=1;continue
    if l.startswith('@@'):flush(f,line,rem,add);rem=[];add=[];line=int(re.search(r'\+(\d+)',l).group(1));continue
    if l.startswith('-') and not l.startswith('---'):rem+=LIT.findall(l[1:])
    elif l.startswith('+') and not l.startswith('+++'):add+=LIT.findall(l[1:])
flush(f,line,rem,add)
for f,line,(kind,tok),n in losses:print(f'LOSS {f}:{line} {kind} {tok!r}')
print(f'checked {hunks} changed hunks in {files} files: {len(losses)} lost tokens')
sys.exit(1 if losses else 0)
