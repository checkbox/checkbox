/*
 * This file is part of plainbox-gui
 *
 * Copyright 2013 Canonical Ltd.
 *
 * Authors:
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

#ifndef PB_NAMES_H
#define PB_NAMES_H

/* Dbus specification standard interface names - they dont appear to be defined
 * by Qt DBus system.
 */

static const QString ofDObjectManagerName("org.freedesktop.DBus.ObjectManager");
static const QString ofDIntrospectableName("org.freedesktop.DBus.Introspectable");
static const QString ofDPropertiesName("org.freedesktop.DBus.Properties");

/* The names for Plainbox top-level DBus structures.
 */
static const QString PBBusName("com.canonical.certification.PlainBox1");
static const QString PBObjectPathName("/plainbox/service1");
static const QString PBInterfaceName("com.canonical.certification.PlainBox.Service1");

// Whitelist interfaces
static const QString PBWhiteListInterface("com.canonical.certification.PlainBox.WhiteList1");

// Session Interfaces
static const QString PBSessionStateInterface("com.canonical.certification.PlainBox.Session1");

// JobRunner Interfaces
static const QString PBJobRunnerInterface("com.canonical.certification.PlainBox.RunningJob1");

// Well-known Plainbox/Checkbox Job Interfaces
static const QString CheckBoxJobDefinition1("com.canonical.certification.CheckBox.JobDefinition1");
static const QString PlainboxJobDefinition1("com.canonical.certification.PlainBox.JobDefinition1");

// JobState interfaces
static const QString JobStateInterface("com.canonical.certification.PlainBox.JobState1");

// JobResult interface
static const QString JobResultInterface("com.canonical.certification.PlainBox.Result1");


// JobResults
static const QString JobResult_OUTCOME_PASS = "pass";
static const QString JobResult_OUTCOME_FAIL = "fail";
static const QString JobResult_OUTCOME_SKIP = "skip";
static const QString JobResult_OUTCOME_NONE = "none";

#endif // PB_NAMES_H
