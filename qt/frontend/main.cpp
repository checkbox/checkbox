#include <QtGui/QApplication>
#include "qtfront.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    a.setWindowIcon(QIcon::fromTheme("checkbox"));
    new QtFront(&a);
    QDBusConnection::sessionBus().registerObject("/QtCheckbox", &a);
    QDBusConnection::sessionBus().registerService("com.canonical.QtCheckbox");
    //w.show();
    
    return a.exec();
}
