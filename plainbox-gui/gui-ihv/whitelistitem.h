/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
 * - Julia Segal <julia.segal@cellsoftware.co.uk>
 * - Andrew Haigh <andrew.haigh@cellsoftware.co.uk>
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
#include "../gui-engine/gui-engine.h"

class WhiteListItem : public ListItem
{
    Q_OBJECT
    Q_PROPERTY(QString testname READ testname WRITE setTestname NOTIFY testnameChanged)
    Q_PROPERTY(bool check READ check WRITE setCheck NOTIFY checkChanged)
    Q_PROPERTY(QString objectpath READ objectpath WRITE setObjectpath NOTIFY objectpathChanged)

signals:
    void testnameChanged();
    void checkChanged();
    void objectpathChanged();

public:
      enum Roles {
        TestNameRole = Qt::UserRole+1,
        CheckRole,
        ObjectPathRole
      };

public:
    WhiteListItem(QObject * parent = 0 ) : ListItem(parent), m_check(true){}
    WhiteListItem(const QString &testname, const QString &opath, QObject * parent = 0 );

    QVariant data(int role) const;
    void setData(const QVariant & value, int role);

    QHash<int, QByteArray> roleNames() const;
    inline QString id() const { return m_testName; }

    inline QString testname() const { return m_testName; }
    void setTestname(const QString &testName);

    inline bool check() const { return m_check; }
    void setCheck(bool check);

    inline QString objectpath() const { return m_path; }
    void setObjectpath(const QString &opath);

private:
    QString m_testName;
    bool m_check;

    // Uniquely and persistently identifies this whitelist
    QString m_path;
};
