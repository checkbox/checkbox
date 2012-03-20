#ifndef QTFRONT_H
#define QTFRONT_H

#include <QWidget>
#include <QtDBus>
#include <QCloseEvent>
#include <QTextEdit>

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
    void showError(QString text);
    void stopProgressBar();
    void showTree(QString text, QVariantMap options);
    void showEntry(QString text);
    QVariantMap getTestsToRun();
    QString getEmailAddress();
    QString getTestComment();
    void showTest(QString purpose, QString steps, QString verification, QString info, QString comment, QString testType, QString testName, bool enableTestButton);
    void showTestControls(bool enableTestControls);
    void setFocusTestYesNo(bool status);
    QString showInfo(QString text, QStringList options, QString defaultoption);
    void setUiFlags(QVariantMap flags);
    void updateAutoTestStatus(QString status, QString testName);

private slots:
    void onFullTestsClicked();
    void onStartTestsClicked();
    void onSubmitTestsClicked();
    void onNextTestClicked();
    void onPreviousTestClicked();
    void onYesTestClicked();
    void onNoTestClicked();
    void onReviewTestsClicked();

    void onJobItemChanged(QModelIndex index);
    void onJobItemChanged(QStandardItem *item, QString job, QModelIndex baseIndex);
    void updateTestStatus(QStandardItem *item, QString status);
    void updateTestStatus(QString status = QString());
    void onSelectAllContextMenu(const QPoint& pos);
    void onClosedFrontend();

signals:
    void fullTestsClicked();
    void startTestsClicked();
    void startTestClicked();
    void yesTestClicked();
    void noTestClicked();
    void nextTestClicked();
    void previousTestClicked();
    void submitTestsClicked();
    void reviewTestsClicked();
    void closedFrontend(bool testsFinished);
    void welcomeCheckboxToggled(bool toogled);

private:
    bool registerService();
    void buildTree(QVariantMap options, QString baseIndex = "1", QStandardItem *parentItem = 0, QStandardItem *parentStatusItem = 0);
    void buildTestsToRun(QStandardItem *item, QString baseIndex, QVariantMap &items);
    Ui_main *ui;
    QWidget *m_mainWindow;
    TreeModel * m_model;
    QStandardItemModel *m_statusModel;
    QTextEdit *m_currentTextComment;
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
