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

#include <qdebug.h>
#include "whitelistitem.h"


WhiteListItem::WhiteListItem(const QString &testName, \
                             const QString &opath, \
                             QObject * parent  ) :
    ListItem( parent ),
    m_testName(testName),
    m_check(true),
    m_path(opath)
{
}

QHash<int, QByteArray> WhiteListItem::roleNames() const
{
  QHash<int, QByteArray> names;
  names[TestNameRole] = "testname";
  names[CheckRole] = "check";
  return names;
}

QVariant WhiteListItem::data(int role) const
{
  switch(role) {
  case TestNameRole:
    return testname();
  case CheckRole:
      return check();
  case ObjectPathRole:
      return objectpath();
  default:
    return QVariant();
  }
}

void WhiteListItem::setData(const QVariant & value, int role){
    switch(role) {
    case TestNameRole:
        setTestname(value.toString());
        break;
    case CheckRole:
        setCheck(value.toBool());
        break;
    case ObjectPathRole:
        setObjectpath(value.toString());
    }
}

void WhiteListItem::setTestname(const QString &testName){
    if ( testName != m_testName ) {
        m_testName = testName;
        emit testnameChanged();
        emit dataChanged();
    }
}

void WhiteListItem::setCheck(bool check){
    if (check != m_check){
        m_check = check;
        emit checkChanged();
        emit dataChanged();
        qDebug() << m_testName << " " << m_path << "check changed to" << check;

        const QString engname("");

        GuiEngine* myengine = qApp->findChild<GuiEngine*>(engname);
        if(myengine == NULL) {
            qDebug("Cant find guiengine object");
            return;
        }

        // Set everything here
        QDBusObjectPath opath(m_path);

        myengine->SetWhiteList(opath, m_check);
    }
}

void WhiteListItem::setObjectpath(const QString &opath){
    if (m_path.compare(opath) != 0 ) {
        m_path = opath;
        emit objectpathChanged();
        emit dataChanged();
    }
}
