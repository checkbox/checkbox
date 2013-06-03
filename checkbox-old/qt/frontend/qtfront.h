#ifndef QTFRONT_H
#define QTFRONT_H

#include <QWidget>
#include <QtDBus>
#include <QCloseEvent>
#include <QTextEdit>

#include "checkboxtr.h"
#include "treemodel.h"

class Ui_main;

class CustomQWidget : QWidget
{
    Q_OBJECT
    void closeEvent(QCloseEvent *event) {
        emit closed();
        event->accept();

    }
signals:
    void closed();
};


class QtFront : public QDBusAbstractAdaptor
{
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "com.canonical.QtCheckbox")

    enum state {
       WELCOME = 0,
       TREE,
       TESTING,
       SUBMISSION
    } currentState;
    
public:
    explicit QtFront(QApplication *application);
    ~QtFront();

public slots:
    void setInitialState();
    void showText(QString text);
    void setWindowTitle(QString title);
    void startProgressBar(QString text);
    Q_NOREPLY void showError(QString primary_text,
                             QString secondary_text,
                             QString detailed_text);
    void stopProgressBar();
    void showTree(QString text, QVariantMap options, QVariantMap defaults, QString deselect_warning);
    void showEntry(QString text, QString value, QString label, bool showSubmitToHexr);
    QVariantMap getTestsToRun();
    QString getSubmissionData();
    bool getSubmitToHexr();
    QString getTestComment();
    void showTest(QString purpose, QString steps, QString verification, QString info, QString comment, QString testStatus, QString testType, QString testName, bool enableTestButton);
    void showTestControls(bool enableTestControls);
    void setTestResult(bool status);
    QString getTestResult();
    Q_NOREPLY void showInfo(QString text, QStringList options, QString defaultoption);
    void updateAutoTestStatus(QString status, QString testName);

private slots:
    void onFullTestsClicked();
    void onDeselectAllClicked();
    void onSelectAllClicked();
    void onTestSelectionChanged(QModelIndex index);
    void onStartTestsClicked();
    void onSubmitTestsClicked();
    void onNextTestClicked();
    void onPreviousTestClicked();
    void onReviewTestsClicked();

    void onJobItemChanged(QModelIndex index);
    void onJobItemChanged(QStandardItem *item, QString job, QModelIndex baseIndex);
    void updateTestStatus(QStandardItem *item, QStandardItem* statusItem, QString status);
    void updateTestStatus(QString status = QString());
    void onClosedFrontend();

signals:
    void fullTestsClicked();
    void startTestsClicked();
    void startTestClicked();
    void nextTestClicked();
    void previousTestClicked();
    void submitTestsClicked();
    void reviewTestsClicked();
    void closedFrontend(bool testsFinished);
    void infoBoxResult(QString result);
    void errorBoxClosed();
    void testSelectionChanged();

private:
    bool registerService();
    void buildTree(QVariantMap options, QVariantMap defaults, QString baseIndex = "1", QStandardItem *parentItem = 0);
    void buildTestsToRun(QStandardItem *item, QString baseIndex, QVariantMap &items);
    Ui_main *ui;
    QWidget *m_mainWindow;
    TreeModel * m_model;
    QStandardItemModel *m_statusModel;
    QMap<QString, QString> m_statusList;
    QMap <QString, QString> m_titleTestTypes;
    QMap <QString, QString> m_statusStrings;
    int m_currentTab;
    bool m_skipTestMessage;
    QString m_currentTestName;
    bool isFirstTimeWelcome;
    bool m_doneTesting;
};

#endif // QTFRONT_H
