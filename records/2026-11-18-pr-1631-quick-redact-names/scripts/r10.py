import sys,json;sys.path.insert(0,'/home/patrick/work/qr1618/bin')
from qrlib import *
O=os.path.expanduser('~/work/qr1618/state/out/')
opid,ins=edit_open('desktop'); save(opid,O+'r10-agent-orig.png')
res_={}
r=apply(opid,[{'op':'redactText','categories':['list'],'terms':['build-host-7']}])
res_['terms']=r.get('result',{}).get('counts') if r.get('ok') else r.get('error')
print('terms ok',r.get('ok'),json.dumps(r.get('result',{}).get('counts')),'created',r.get('result',{}).get('created'),'skipped',r.get('result',{}).get('skippedPatterns'))
save(opid,O+'r10-agent-red.png')
i=inspect(opid); json.dump({'shapes':[{'rect':s['rect'],'suggested':s.get('suggested')} for s in i['shapes']]},open(O+'r10-agent.json','w'))
SECRET='(ZQXJsecretword'
for label,cmd in [('badpattern',{'op':'redactText','categories':['list'],'patterns':['ok-\\d+',SECRET]}),
                  ('badpattern_first',{'op':'redactText','categories':['list'],'patterns':[SECRET]}),
                  ('toomanychars',{'op':'redactText','categories':['list'],'patterns':['x'*501]}),
                  ('emptymatch',{'op':'redactText','categories':['list'],'patterns':['a*']}),
                  ('bad_terms_linebreak',{'op':'redactText','categories':['list'],'terms':['ab\ncd']}),
                  ('eight_categories',{'op':'redactText','categories':['email','phone','ip','card','key','name','list','list']}),
                  ('unknown_category',{'op':'redactText','categories':['bogus']})]:
    r=apply(opid,[cmd]); txt=json.dumps(r)
    res_[label]={'ok':r.get('ok'),'error':r.get('error'),'leaks_pattern_text':('ZQXJ' in txt or 'secretword' in txt),'created':(r.get('result') or {}).get('created')}
    print(label,'ok',r.get('ok'),json.dumps(r.get('error')),'LEAK' if res_[label]['leaks_pattern_text'] else 'no-leak')
json.dump(res_,open(O+'r10-agent-errors.json','w'),indent=1)
open(O+'current-op','w').write(opid)
