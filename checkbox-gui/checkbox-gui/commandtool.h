/*
 * This file is part of Checkbox
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef COMMANDTOOL_H
#define COMMANDTOOL_H

#include <QObject>
#include <QProcess>
#include <qdebug.h>

class CommandTool : public QObject
{
    Q_OBJECT
public:
    explicit CommandTool(QObject *parent = 0);
    Q_INVOKABLE void exec(const QString& cmd, const QString &args);

private:
    QProcess *m_process;
};

#endif // COMMAND_H
