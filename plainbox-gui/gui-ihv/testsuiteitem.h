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
    Q_PROPERTY(int duration READ duration WRITE setDuration NOTIFY durationChanged)
    Q_PROPERTY(QString type READ type)
    Q_PROPERTY(int runStatus READ runstatus WRITE setRunstatus NOTIFY runstatusChanged)
    Q_PROPERTY(int elapsedtime READ elapsedtime WRITE setElapsedtime NOTIFY elapsedtimeChanged)
    Q_PROPERTY(int groupstatus READ groupstatus WRITE setGroupstatus NOTIFY groupstatusChanged)



signals:
    void groupChanged();
    void testnameChanged();
    void checkChanged();
    void durationChanged();
    void runstatusChanged();
    void elapsedtimeChanged();
    void groupstatusChanged();

public:
      enum Roles {
        GroupRole = Qt::UserRole+1,
        TestNameRole,
        CheckRole,
        DurationRole,
        TypeRole,
        RunstatusRole,
        ElapsedtimeRole,
        GroupstatusRole
      };


public:
    TestSuiteItem(QObject * parent = 0 ) : ListItem(parent), m_check(true), m_runstatus(0), m_elapsedtime(0), m_groupstatus(0){}
    TestSuiteItem(const QString &groupName, const QString &testname, int durationInSeconds, const QString &type, QObject * parent = 0 );

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

    inline int duration() const { return m_duration; }
    void setDuration(int duration);

    inline QString type() const {return m_type; }

    inline int runstatus() const { return m_runstatus; }
    void setRunstatus(int runstatus);

    inline int elapsedtime() const { return m_elapsedtime; }
    void setElapsedtime(int elapsedtime);

    inline int groupstatus() const {return m_groupstatus; }
    void setGroupstatus(int groupstatus);



private:
    QString m_group;
    QString m_testName;
    bool m_check;
    int m_duration;
    QString m_type;
    int m_runstatus;
    int m_elapsedtime;
    int m_groupstatus;
};




