import pass2 as p,rfb,sys,time,json,subprocess
P=p.P;host=sys.argv[1];v=rfb.RFB(5901 if host=='f44' else 5900)
p.rpc('ui.show',{'view':'settings'});time.sleep(2)
v.screenshot(P/'settings-general.png');(P/'settings-view.json').write_text(json.dumps(p.rpc('ui.viewState'),indent=2))
