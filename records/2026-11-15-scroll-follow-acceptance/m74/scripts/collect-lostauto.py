import accept as A,json,shutil
P=A.P;v=next(x['value'] for x in json.loads((P/'lostauto-results.json').read_text()) if x['label']=='end')
sid=v['id'];records=A.rpc('history.list')['records'];r=next(x for x in records if x['operationId']==sid);src=P/'archive'/r['category']/r['name'];assert str(src)==r['local']['path'];shutil.copyfile(src,P/'lostauto-capture.png');(P/'lostauto-operation.json').write_text(json.dumps({'operation':v,'history':r},indent=1));print('preserved',sid,src.stat().st_size)
