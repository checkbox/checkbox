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

#include "testsuiteitem.h"

TestSuiteItem::TestSuiteItem(const QString &groupName, const QString &testName, QObject * parent  ) :
        QObject( parent ),
        m_group(groupName),
        m_testName(testName)
{
}

void TestSuiteItem::setGroup(const QString &groupName){
    if ( groupName != m_group ) {
        m_group = groupName;
        emit groupChanged();
    }
}

void TestSuiteItem::setTestname(const QString &testName){
    if ( testName != m_testName ) {
        m_testName = testName;
        emit testnameChanged();
    }  }


