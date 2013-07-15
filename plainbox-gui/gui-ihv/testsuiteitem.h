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
#include "listmodel.h"


class TestSuiteItem : public ListItem
{
    Q_OBJECT
    Q_PROPERTY(QString group READ group WRITE setGroup NOTIFY groupChanged)
    Q_PROPERTY(QString testname READ testname WRITE setTestname NOTIFY testnameChanged)
    Q_PROPERTY(bool check READ check WRITE setCheck NOTIFY checkChanged)

signals:
    void groupChanged();
    void testnameChanged();
    void checkChanged();

public:
      enum Roles {
        GroupRole = Qt::UserRole+1,
        TestNameRole,
        CheckRole
      };


public:
    TestSuiteItem(QObject * parent = 0 ) : ListItem(parent), m_check(true){}
    TestSuiteItem(const QString &groupName, const QString &testname, QObject * parent = 0 );

    QVariant data(int role) const;
    void setData(const QVariant & value, int role);

    QHash<int, QByteArray> roleNames() const;
    inline QString id() const { return m_testName; }

    inline QString group() const { return m_group; }
    void setGroup(const QString &groupName);

    inline QString testname() const { return m_testName; }
    void setTestname(const QString &testName);

    inline bool check() const { return m_check; }
    void setCheck(bool check);


private:
    QString m_group;
    QString m_testName;
    bool m_check;

};




