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

#include "test-gui-engine.h"

void TestGuiEngine::TestInitialise()
{
    QVERIFY(Initialise());
}

void TestGuiEngine::TestGetWhiteListPathsAndNames()
{
    QMap<QDBusObjectPath,QString> whitenames;

    whitenames = GetWhiteListPathsAndNames();

    QVERIFY(whitenames.count() != 0);
}

void TestGuiEngine::TestGetJobsNames()
{
    // we should connect a reciever to the LocalJobsCompleted() signal
    connect(this, SIGNAL(localJobsCompleted(void)), this, SLOT(AcknowledgeJobsDone()));

    RunLocalJobs();

    // Now, spin the loop to process Job completion signals from Plainbo
    while(!m_local_jobs_done) {
        QTest::qWait(1);   // spin for 1ms in the event loop
    }
    LogDumpTree();
}

void TestGuiEngine::TestShutdown()
{
    QVERIFY(Shutdown());
}

QTEST_MAIN(TestGuiEngine)

