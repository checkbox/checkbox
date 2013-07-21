/*
 * This file is part of plainbox-gui
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

#ifndef LAUNCHGEDIT_H
#define LAUNCHGEDIT_H

#include <QObject>
#include <QProcess>
#include <qdebug.h>

class LaunchGEdit : public QObject
{
    Q_OBJECT
public:
    explicit LaunchGEdit(QObject *parent = 0);
    Q_INVOKABLE void launch(const QString& filename);

private:
    QProcess *m_process;
};

#endif // LAUNCHGEDIT_H
