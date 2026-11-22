import json,sys
a={r['id']:r for r in json.load(open(sys.argv[1]+'/rows.json'))}
b={r['id']:r for r in json.load(open(sys.argv[2]+'/rows.json'))}
same=sum(1 for i in a if i in b and a[i].get('text')==b[i].get('text') and 'text' in a[i])
diff=[i for i in a if i in b and a[i].get('text')!=b[i].get('text')]
print('ids',len(a),len(b),'identical text',same,'differ',len(diff),diff[:10])
