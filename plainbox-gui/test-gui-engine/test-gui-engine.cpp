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

void TestGuiEngine::TestRunLocalJobs()
{
    // we should connect a receiver to the LocalJobsCompleted() signal
    connect(this, SIGNAL(localJobsCompleted(void)), this, SLOT(AcknowledgeLocalJobsDone()));

    RunLocalJobs();

    // Now, spin the loop to process Job completion signals from Plainbo
    while(!m_local_jobs_done) {
        QTest::qWait(1);   // spin for 1ms in the event loop
    }

    // For interest
    GetJobTreeNodes()->LogDumpTree(GetValidRunList());

    // we should disconnect a the old receiver of the localJobsCompleted() signal
    disconnect(this, SIGNAL(localJobsCompleted(void)), this, SLOT(AcknowledgeLocalJobsDone()));
}

void TestGuiEngine::TestRunJobs()
{
    // we should connect a reciever to the jobsCompleted() signal
    connect(this, SIGNAL(jobsCompleted(void)), this, SLOT(AcknowledgeJobsDone()));

    // We should also connect the manual interaction signal
    connect(this,SIGNAL(raiseManualInteractionDialog(int)),this,SLOT(ManualTest(int)));

    // We should also connect the update manual interaction signal
    connect(this,SIGNAL(updateManualInteractionDialog(int)),this,SLOT(ManualTest(int)));

	PrepareJobs();

    // Now, we want to run all the real jobs
    RunJobs();

    // Now, spin the loop to process Job completion signals from Plainbo
    while(!m_jobs_done) {
        QTest::qWait(1);   // spin for 1ms in the event loop
    }
}

void TestGuiEngine::TestGetResults()
{
    QString format = "text";
    QStringList options;    // No options needed

    qDebug() << ExportSession(GetCurrentSession(),format,options);
}

void TestGuiEngine::TestShutdown()
{
    QVERIFY(Shutdown());
}

QTEST_MAIN(TestGuiEngine)

