#include "commandtool.h"

CommandTool::CommandTool(QObject *parent) :
    QObject(parent),
    m_process(new QProcess(this))
{
}


void CommandTool::exec(const QString& cmd, const QString& args)
{
    QStringList arguments;
    arguments << args;
    m_process->start(cmd, arguments);
}
