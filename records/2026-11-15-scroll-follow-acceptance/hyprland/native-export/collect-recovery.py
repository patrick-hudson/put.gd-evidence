import accept as A,json,shutil,hashlib,sys
P=A.P;prefix=sys.argv[1]
v=next(x['value'] for x in json.loads((P/(prefix+'-results.json')).read_text()) if x['label']=='end')
import find_history;r=find_history.find_operation(A,v['id']);src=A.Path(r['local']['path']);assert hashlib.sha256(src.read_bytes()).hexdigest()==r['sha256'];shutil.copyfile(src,P/(prefix+'-capture.png'));(P/(prefix+'-operation.json')).write_text(json.dumps({'operation':v,'history':r},indent=1));print('preserved',prefix,v['id'])
