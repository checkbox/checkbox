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

#include <QObject>


class TestSuiteItem : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString group READ group WRITE setGroup NOTIFY groupChanged)
    Q_PROPERTY(QString testname READ testname WRITE setTestname NOTIFY testnameChanged)

public:
    TestSuiteItem(QObject * parent = 0 ) : QObject(parent){}
  TestSuiteItem(const QString &groupName, const QString &testname, QObject * parent = 0 );

  inline QString group() const { return m_group; }
  void setGroup(const QString &groupName);

  inline QString testname() const { return m_testName; }
  void setTestname(const QString &testName);

signals:
    void groupChanged();
    void testnameChanged();

private:
  QString m_group;
  QString m_testName;

};

