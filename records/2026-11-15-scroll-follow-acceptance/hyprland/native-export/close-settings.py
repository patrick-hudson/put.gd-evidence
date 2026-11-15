import accept as A,time
import rfb
# Only our private local-only resident's Settings window is raised and closed.
A.rpc('ui.show',{'view':'settings'});time.sleep(2)
v=rfb.RFB(5900);v.screenshot(A.P/'settings-before-close.png');v.key('alt','f4');time.sleep(2);v.screenshot(A.P/'settings-after-close.png');v.close()
assert A.rpc('diagnostics')['build']['gitTree']==A.os.environ.get('SFA_EXPECT_TREE','bd64ffc5ac593690430bdbabb7e1f9ce6964de7e')
print('Private resident alive after normal native Settings window close',flush=True)
