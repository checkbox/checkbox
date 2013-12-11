/*
 * This file is part of Checkbox
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

#include <qdebug.h>
#include "../gui-engine/PBNames.h"
#include "testitem.h"


TestItem::TestItem(const double &duration, \
                   const QString &checksum, \
                   const QString &depends, \
                   const QString &testname, \
                   const QString &requires, \
                   const QString &description, \
                   const QString &command, \
                   const QString &environ, \
                   const QString &plugin, \
                   const QString &type, \
                   const QString &user, \
                   const QString &via, \
                   const QString &group, \
                   const bool &check, \
                   const QString &path, \
                   const QList<QString> &parent_names, \
                   const QList<QString> &parent_ids, \
                   const int &depth, \
                   const bool &branch, \
                   const bool &rerun, \
                   QObject * parent  ) :
    ListItem(parent), \
              m_duration(duration), \
              m_checksum(checksum), \
              m_depends(depends), \
              m_testName(testname), \
              m_requires(requires), \
              m_description(description), \
              m_command(command), \
              m_environ(environ), \
              m_plugin(plugin), \
              m_type(type), \
              m_user(user), \
              m_via(via), \
              m_group(group), \
              m_check(check), \
              m_path(path), \
              m_parent_names(parent_names), \
              m_parent_ids(parent_ids), \
              m_depth(depth), \
              m_branch(branch), \
          m_runstatus(0),
          m_elapsedtime(0),
              m_groupstatus(0),
              m_rerun(true) // covers the first run of all the tests
{
    // FIXME - Hard-coded data whilst we correct the RunManagerTestDelegate
    m_outcome = JobResult_OUTCOME_PASS;
    m_comments = "No comment set";
    m_io_log = "IO Log not set";
}

QHash<int, QByteArray> TestItem::roleNames() const
{
  QHash<int, QByteArray> names;

  names[DurationRole] = "duration";
  names[ChecksumRole] = "checksum";
  names[DependsRole] = "depends";
  names[TestNameRole] = "testname";
  names[RequiresRole] = "requires";
  names[DescriptionRole] = "description";

  names[CommandRole] = "command";
  names[EnvironRole] = "environ";
  names[PluginRole] = "plugin";
  names[TypeRole] = "type";
  names[UserRole] = "user";
  names[ViaRole] = "via";

  names[GroupRole] = "group";
  names[CheckRole] = "check";
  names[ObjectPathRole] = "objectpath";

  names[RunstatusRole] = "runstatus";
  names[ElapsedtimeRole] = "elapsedtime";
  names[GroupstatusRole] = "groupstatus";

  names[ParentNameRole] = "parentname";
  names[ParentIdRole] = "parentid";
  names[DepthRole] = "depth";
  names[BranchRole] = "branch";

  names[IOLogRole] = "io_log";
  names[CommentsRole] = "comments";
  names[OutcomeRole] = "outcome";

  names[RerunRole] = "rerun";

  return names;
}

QVariant TestItem::data(int role) const
{
  switch(role) {
  case DurationRole:
      return duration();
  case ChecksumRole:
    return checksum();
  case DependsRole:
    return depends();
  case TestNameRole:
    return testname();
  case RequiresRole:
    return requires();
  case DescriptionRole:
      return description();

  case CommandRole:
      return command();
  case EnvironRole:
      return environ();
  case PluginRole:
      return plugin();
  case TypeRole:
      return type();
  case UserRole:
      return user();
  case ViaRole:
      return via();

  case GroupRole:
      return group();
  case CheckRole:
      return check();
  case ObjectPathRole:
      return objectpath();
  case RunstatusRole:
      return runstatus();
  case ElapsedtimeRole:
      return elapsedtime();
  case GroupstatusRole:
      return groupstatus();

  case ParentNameRole:
//      return parentnamelist();
      break;

  case ParentIdRole:
//       return parentidlist();
    break;

  case DepthRole:
      return depth();

  case BranchRole:
      return branch();

  case RerunRole:
      return rerun();

  default:
    return QVariant();
  }

  // Prevents non-void return warning from the compiler
  return QVariant();
}

void TestItem::setData(const QVariant & value, int role){
    switch(role) {

    case DurationRole:
        setDuration(value.toDouble());
        break;

    case ChecksumRole:
        setChecksum(value.toString());
        break;

    case DependsRole:
        setDepends(value.toString());
        break;

    case TestNameRole:
        setTestname(value.toString());
        break;

    case RequiresRole:
        setRequires(value.toString());
        break;

    case DescriptionRole:
        setDescription(value.toString());
        break;



    case CommandRole:
        setCommand(value.toString());
        break;

    case EnvironRole:
        setEnviron(value.toString());
        break;

    case PluginRole:
        setPlugin(value.toString());
        break;

    case TypeRole:
        setType(value.toString());
        break;

    case UserRole:
        setUser(value.toString());
        break;

    case ViaRole:
        setVia(value.toString());
        break;



    case GroupRole:
        setGroup(value.toString());
        break;

    case CheckRole:
        setCheck(value.toBool());
        break;

    case ObjectPathRole:
        setObjectpath(value.toString());
    break;

    case RunstatusRole:
        setRunstatus(value.toInt());
        break;
    case ElapsedtimeRole:
        setElapsedtime(value.toInt());
        break;
    case GroupstatusRole:
        setGroupstatus(value.toInt());
        break;

    case ParentNameRole:
        //setGroupstatus(value.toStringList()));
        break;

    case ParentIdRole:
        //setGroupstatus(value.toStringList());
        break;

    case DepthRole:
        setDepth(value.toInt());
        break;

    case BranchRole:
        setBranch(value.toBool());
        break;

    case IOLogRole:
        setIo_log(value.toString());
        break;

    case CommentsRole:
        setComments(value.toString());
        break;

    case OutcomeRole:
        setOutcome(value.toString());
        break;

    case RerunRole:
        setRerun(value.toBool());
        break;
    }
}

void TestItem::setGroup(const QString &groupName){
    if ( groupName != m_group ) {
        m_group = groupName;
        emit groupChanged();
        emit dataChanged();
    }
}

void TestItem::setRequires(const QString &requires){
    if ( requires != m_requires ) {
        m_requires = requires;
        emit requiresChanged();
        emit dataChanged();
    }
}

void TestItem::setDescription(const QString &description){
    if (description.compare(description) != 0 ) {
        m_description = description;
        emit descriptionChanged();
        emit dataChanged();
    }
}

void TestItem::setTestname(const QString &testName){
    if ( testName != m_testName ) {
        m_testName = testName;
        emit testnameChanged();
        emit dataChanged();
    }
}

void TestItem::setCheck(bool check){
    if (check != m_check){
        m_check = check;
        emit checkChanged();
        emit dataChanged();
    }
}

void TestItem::setDuration(int duration){
    if (duration != m_duration){
        m_duration = duration;
        emit durationChanged();
        emit dataChanged();
    }
}

void TestItem::setObjectpath(const QString &opath){
    if (m_path.compare(opath) != 0 ) {
        m_path = opath;
        emit objectpathChanged();
        emit dataChanged();
    }
}

void TestItem::setChecksum(const QString &checksum){
    if (checksum.compare(checksum) != 0 ) {
        m_checksum = checksum;
        emit checksumChanged();
        emit dataChanged();
    }
}

void TestItem::setDepends(const QString &depends){
    if (depends.compare(depends) != 0 ) {
        m_depends = depends;
        emit dependsChanged();
        emit dataChanged();
    }
}

void TestItem::setCommand(const QString &command){
    if (command.compare(command) != 0 ) {
        m_command = command;
        emit commandChanged();
        emit dataChanged();
    }
}

void TestItem::setEnviron(const QString &environ){
    if (environ.compare(environ) != 0 ) {
        m_environ = environ;
        emit environChanged();
        emit dataChanged();
    }
}

void TestItem::setPlugin(const QString &plugin){
    if (plugin.compare(plugin) != 0 ) {
        m_plugin = plugin;
        emit pluginChanged();
        emit dataChanged();
    }
}

void TestItem::setType(const QString &type){
    if (type.compare(type) != 0 ) {
        m_type = type;
        emit typeChanged();
        emit dataChanged();
    }
}

void TestItem::setUser(const QString &user){
    if (user.compare(user) != 0 ) {
        m_user = user;
        emit userChanged();
        emit dataChanged();
    }
}

void TestItem::setVia(const QString &via){
    if (via.compare(via) != 0 ) {
        m_via = via;
        emit viaChanged();
        emit dataChanged();
    }
}

void TestItem::setElapsedtime(int elapsedtime){
    if (elapsedtime != m_elapsedtime){
        m_elapsedtime = elapsedtime;
        emit elapsedtimeChanged();
        emit dataChanged();
    }
}

void TestItem::setRunstatus(int runstatus){
    if (runstatus != m_runstatus){
        m_runstatus = runstatus;
        emit runstatusChanged();
        emit dataChanged();
    }
}

void TestItem::setGroupstatus(int groupstatus){
    if (groupstatus != m_groupstatus){
        m_groupstatus = groupstatus;
        emit groupstatusChanged();
        emit dataChanged();
    }
}

void TestItem::setParentnamelist(const QList<QString> &parent_names){
    if (parent_names != m_parent_names){
        m_parent_names = parent_names;
        emit parentnamelistChanged();
        emit dataChanged();
    }
}

void TestItem::setParentidlist(const QList<QString> &parent_ids){
    if (parent_ids != m_parent_ids){
        m_parent_ids = parent_ids;
        emit parentnamelistChanged();
        emit dataChanged();
    }
}

void TestItem::setDepth(int depth){
    if (depth != m_depth){
        m_depth = depth;
        emit depthChanged();
        emit dataChanged();
    }
}

void TestItem::setBranch(bool branch){
    if (branch != m_branch){
        m_branch = branch;
        emit branchChanged();
        emit dataChanged();
    }
}

void TestItem::setIo_log(const QString &io_log){
    if (m_io_log.compare(io_log) != 0 ) {
        m_io_log = io_log;
        emit io_logChanged();
        emit dataChanged();
    }
}

void TestItem::setComments(const QString &comments){
    if (m_comments.compare(comments) != 0 ) {
        m_comments = comments;
        emit commentsChanged();
        emit dataChanged();
    }
}

void TestItem::setOutcome(const QString &outcome){
    if (m_outcome.compare(outcome) != 0 ) {
        m_outcome = outcome;
        emit outcomeChanged();
        emit dataChanged();
    }
}

void TestItem::setRerun(bool rerun){
    if (rerun != m_rerun){
        m_rerun = rerun;
        emit rerunChanged();
        emit dataChanged();
    }
}
