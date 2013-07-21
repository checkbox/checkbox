#include "launchgedit.h"

LaunchGEdit::LaunchGEdit(QObject *parent) :
    QObject(parent),
    m_process(new QProcess(this))
{
}


void LaunchGEdit::launch(const QString& filename)
{
    QString program = "gedit";
    QStringList arguments;
    arguments << filename;
    m_process->setWorkingDirectory("~/");
    m_process->start(program, arguments);
}
