#include <QtGui/QApplication>
#include "checkboxtr.h"
#include "qtfront.h"

int main(int argc, char *argv[])
{
    trInit("checkbox","/usr/share/locale/");

    QApplication a(argc, argv);
    a.setWindowIcon(QIcon::fromTheme("checkbox"));
    new QtFront(&a);

    QDBusConnection::sessionBus().registerObject("/QtCheckbox", &a);
    QDBusConnection::sessionBus().registerService("com.canonical.QtCheckbox");
    //w.show();
    
    return a.exec();
}
