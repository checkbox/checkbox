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

#include <qdebug.h>
#include "testsuiteitem.h"


TestSuiteItem::TestSuiteItem(const QString &groupName, const QString &testName, int duration, const QString &type, QObject * parent  ) :
    ListItem( parent ),
    m_group(groupName),
    m_testName(testName),
    m_check(true),
    m_duration(duration),
    m_type(type)
{
}

QHash<int, QByteArray> TestSuiteItem::roleNames() const
{
  //qDebug() << "!!! TestSuiteItem RoleNames";
  QHash<int, QByteArray> names;
  names[GroupRole] = "group";
  names[TestNameRole] = "testname";
  names[CheckRole] = "check";
  names[DurationRole] = "duration";
  names[TypeRole] = "type";
  return names;
}

QVariant TestSuiteItem::data(int role) const
{
  switch(role) {
  case GroupRole:
    return group();
  case TestNameRole:
    return testname();
  case CheckRole:
      return check();
  case DurationRole:
      return duration();
  case TypeRole:
      return type();
  default:
    return QVariant();
  }
}

void TestSuiteItem::setData(const QVariant & value, int role){
    switch(role) {
    case GroupRole:
        setGroup(value.toString());
        break;
    case TestNameRole:
        setTestname(value.toString());
        break;
    case CheckRole:
        setCheck(value.toBool());
        break;
    case DurationRole:
        setDuration(value.toInt());
        break;
    }

}




void TestSuiteItem::setGroup(const QString &groupName){
    if ( groupName != m_group ) {
        m_group = groupName;
        emit groupChanged();
        emit dataChanged();
    }
}

void TestSuiteItem::setTestname(const QString &testName){
    if ( testName != m_testName ) {
        m_testName = testName;
        emit testnameChanged();
        emit dataChanged();
    }
}

void TestSuiteItem::setCheck(bool check){
    if (check != m_check){
        m_check = check;
        emit checkChanged();
        emit dataChanged();
        //qDebug() << m_testName << "check changed to" << check;
    }
}

void TestSuiteItem::setDuration(int duration){
    if (duration != m_duration){
        m_duration = duration;
        emit durationChanged();
        emit dataChanged();
    }
}

