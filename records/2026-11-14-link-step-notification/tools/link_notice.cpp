// Scratch harness, never committed (#1399 follow-up picture): the real OperationService and
// TrayController of this tree with a fixture destination whose link step answers `unknown`.
// One clipboard upload; the desktop's own notification server shows the completion.
#include "fixtures/U2Fixtures.h"
#include "ui/TrayController.h"
#include <QApplication>
#include <QTimer>
using namespace putgd;
using namespace putgd::test;
class LinkStepProvider final:public StorageProvider {
public:
 OpaqueProvider storage;
 ProviderCapabilities capabilities(const Destination& d)const override{auto c=storage.capabilities(d);c.sharing=true;return c;}
 QString serializationKey(const Destination& d,const QJsonObject& o,const QString& n)const override{return storage.serializationKey(d,o,n);}
 Error validateSettings(const QJsonObject& s)const override{return storage.validateSettings(s);}
 void checkName(const Destination& d,const QString& n,std::function<void(NameCheck)> cb,std::shared_ptr<std::atomic_bool> c={})override{storage.checkName(d,n,cb,c);}
 void upload(const UploadRequest& r,std::function<void(UploadResult)> cb)override{storage.upload(r,[cb](UploadResult result){result.receipt.directUrl.clear();cb(result);});}
 void stat(const StorageReceipt& r,std::function<void(StatResult)> cb)override{storage.stat(r,cb);}
 void reconcile(const UploadRequest& r,std::function<void(StatResult)> cb)override{storage.reconcile(r,cb);}
 void remove(const DeleteRequest& r,DurableCheckpoint d,std::function<void(DeleteResult)> cb)override{storage.remove(r,d,cb);}
 void share(const ShareRequest& r,DurableCheckpoint durable,std::function<void(ShareResult)> cb)override{
  durable({{"schemaVersion",1},{"phase","intent"}},[r,cb](Error){auto receipt=r.receipt;receipt.directUrl.clear();cb({"unknown",receipt,{},{}});});
 }
};
int main(int argc,char** argv){
 QApplication app(argc,argv);
 QTemporaryDir dir;ProviderRegistry providers;auto provider=std::make_shared<LinkStepProvider>();providers.add("opaque",provider);
 SettingsService settings(dir.filePath("config.json"),[&](auto id,auto value){return providers.validate(id,value);});
 if(settings.save(configuration(dir.path()),{}).error){qCritical("settings");return 2;}
 Source source;source.payload=textPayload();OperationService operations(dir.filePath("data"),settings,providers,source);
 TrayController controller(operations,[](const QString&){},[]{});
 QTimer poll;QObject::connect(&poll,&QTimer::timeout,&app,[&]{if(!operations.ready())return;poll.stop();
  operations.invoke("clipboard",[](Error e,QJsonObject d){qInfo("invoked %s %s",qPrintable(e.code),qPrintable(d["operationId"].toString()));});});
 poll.start(100);
 QTimer::singleShot(std::stoi(argc>1?argv[1]:"20000"),&app,&QApplication::quit);
 return app.exec();
}
