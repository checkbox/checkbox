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


class TestItem : public ListItem
{
    Q_OBJECT
    // From com.canonical.certification.PlainBox.JobDefinition1 - properties
    Q_PROPERTY(double duration READ duration WRITE setDuration NOTIFY durationChanged)
    Q_PROPERTY(QString checksum READ checksum WRITE setChecksum NOTIFY checksumChanged)
    Q_PROPERTY(QString depends READ depends WRITE setDepends NOTIFY dependsChanged)
    Q_PROPERTY(QString testname READ testname WRITE setTestname NOTIFY testnameChanged)
    Q_PROPERTY(QString requires READ requires WRITE setRequires NOTIFY requiresChanged)
    Q_PROPERTY(QString description READ description WRITE setDescription NOTIFY descriptionChanged)

    // From com.canonical.certification.CheckBox.JobDefinition1 - properties
    Q_PROPERTY(QString command READ command WRITE setCommand NOTIFY commandChanged)
    Q_PROPERTY(QString environ READ environ WRITE setEnviron NOTIFY environChanged)
    Q_PROPERTY(QString type READ type WRITE setType NOTIFY typeChanged)
    Q_PROPERTY(QString user READ user WRITE setUser NOTIFY userChanged)
    Q_PROPERTY(QString via READ via WRITE setVia NOTIFY viaChanged)

    // Internally required stuff
    Q_PROPERTY(QString group READ group WRITE setGroup NOTIFY groupChanged)
    Q_PROPERTY(bool check READ check WRITE setCheck NOTIFY checkChanged)
    Q_PROPERTY(int duration READ duration WRITE setDuration NOTIFY durationChanged)
    Q_PROPERTY(QString type READ type)
    Q_PROPERTY(int runStatus READ runstatus WRITE setRunstatus NOTIFY runstatusChanged)
    Q_PROPERTY(int elapsedtime READ elapsedtime WRITE setElapsedtime NOTIFY elapsedtimeChanged)
    Q_PROPERTY(int groupstatus READ groupstatus WRITE setGroupstatus NOTIFY groupstatusChanged)
    Q_PROPERTY(QString objectpath READ objectpath WRITE setObjectpath NOTIFY objectpathChanged)



signals:
    void durationChanged();
    void checksumChanged();
    void dependsChanged();
    void testnameChanged();
    void requiresChanged();
    void descriptionChanged();

    void commandChanged();
    void environChanged();
    void typeChanged();
    void userChanged();
    void viaChanged();

    void groupChanged();
    void checkChanged();
    void objectpathChanged();
    void runstatusChanged();
    void elapsedtimeChanged();
    void groupstatusChanged();

public:
    enum Roles {
        // PlainBox.JobDefinition1
        DurationRole = Qt::UserRole+1,
        ChecksumRole,
        DependsRole,
        TestNameRole,
        RequiresRole,
        DescriptionRole,

        // CheckBox.JobDefinition1
        CommandRole,
        EnvironRole,
        TypeRole,
        UserRole,
        ViaRole,

        // Internally required
        GroupRole,
        CheckRole,
        ObjectPathRole,

        RunstatusRole,
        ElapsedtimeRole,
        GroupstatusRole
    };


public:
    TestItem(QObject * parent = 0 ) : ListItem(parent), m_check(true), m_runstatus(0), m_elapsedtime(0), m_groupstatus(0){}
    TestItem(const double &duration, \
             const QString &checksum, \
             const QString &depends, \
             const QString &testname, \
             const QString &requires, \
             const QString &description, \
             const QString &command, \
             const QString &environ, \
             const QString &type, \
             const QString &user, \
             const QString &group, \
             const bool &check, \
             const QString &path, \
             QObject * parent = 0 );

    QVariant data(int role) const;
    void setData(const QVariant & value, int role);

    QHash<int, QByteArray> roleNames() const;
    inline QString id() const { return m_testName; }

    // Duration
    inline double duration() const { return m_duration; }
    void setDuration(int duration);

    // Checksum
    inline QString checksum() const { return m_checksum; }
    void setChecksum(const QString &checksum);

    // Depends
    inline QString depends() const { return m_depends; }
    void setDepends(const QString &depends);

    // testname
    inline QString testname() const { return m_testName; }
    void setTestname(const QString &testName);

    // Requires
    inline QString requires() const { return m_requires; }
    void setRequires(const QString &requires);

    // Description
    inline QString description() const { return m_description; }
    void setDescription(const QString &description);

    // Command
    inline QString command() const {return m_command; }
    void setCommand(const QString &command);

    // Environ
    inline QString environ() const {return m_environ; }
    void setEnviron(const QString &environ);

    // Type
    inline QString type() const {return m_type; }
    void setType(const QString &type);

    // User
    inline QString user() const {return m_user; }
    void setUser(const QString &user);

    // Via
    inline QString via() const {return m_via; }
    void setVia(const QString &via);



    // Group
    inline QString group() const { return m_group; }
    void setGroup(const QString &groupName);

    // Check
    inline bool check() const { return m_check; }
    void setCheck(bool check);

    // ObjectPath
    inline QString objectpath() const { return m_path; }
    void setObjectpath(const QString &opath);

    inline int runstatus() const { return m_runstatus; }
    void setRunstatus(int runstatus);

    inline int elapsedtime() const { return m_elapsedtime; }
    void setElapsedtime(int elapsedtime);

    inline int groupstatus() const {return m_groupstatus; }
    void setGroupstatus(int groupstatus);

private:
    // From com.canonical.certification.PlainBox.JobDefinition1 - properties

    double m_duration;  // estimated_duration
    QString m_checksum; // checksum
    QString m_depends;  // depends
    QString m_testName; // name
    QString m_requires; // requires
    QString m_description;  // description

    // From com.canonical.certification.CheckBox.JobDefinition1 - properties
    QString m_command;  // command
    QString m_environ;  // environ
    QString m_type;     // plugin
    QString m_user;     // user
    QString m_via;      // via

    // Internally required stuff
    QString m_group;    // top-level test grouping

    bool m_check;   // Selected to be run?

    QString m_path; // ObjectPath for this job

    int m_runstatus;
    int m_elapsedtime;
    int m_groupstatus;
};




