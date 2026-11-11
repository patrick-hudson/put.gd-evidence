exec(open('/home/patrick/work/svm1398/v3recover.py').read().split('for k,ident')[0])
for k,i in [('n','8eca03bb-1166-46d1-a3f6-db5a3b3c050c'),('k','9fe5c5b5-8d55-4977-b84d-fb9fbbabf33d')]:
 r=B/'repo/work/lab-runs'/(k+'3');print(k,lab.guest_session(r,'python3 /home/lab/v3guest.py rpc scroll.inspect '+shlex.quote(json.dumps({'id':i}))+'; echo INSPECTED'))
