#ifndef QTFRONT_H
#define QTFRONT_H

#include <QWidget>
#include <QtDBus>
#include <QCloseEvent>

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
    void onFullTestsClicked();
    void onStartTestsClicked();
    void onSubmitTestsClicked();
    void onNextTestClicked();

    void showText(QString text);
    void setWindowTitle(QString title);
    void startProgressBar(QString text);
    void showError(QString text);
    void stopProgressBar();
    void showTree(QString text, QMap<QString, QVariant> options);
    void showEntry(QString text);
    QVariantMap getTestsToRun();
    QString getEmailAddress();
    void showTest(QString purpose, QString steps, QString verification, QString info, QString testType, bool enableTestButton);
    QString showInfo(QString text, QStringList options, QString defaultoption);

private slots:
    void onTabChanged(int index);

signals:
    void fullTestsClicked();
    void startTestsClicked();
    void startTestClicked();
    void yesTestClicked();
    void noTestClicked();
    void nextTestClicked();
    void previousTestClicked();
    void submitTestsClicked();
    // when the user clicks welcome during the tests
    void welcomeScreenRequested();
    // when the user clicks welcome from the tests selection tree
    void welcomeClicked();
    void closedFrontend();

private:
    bool registerService();
    Ui_main *ui;
    QWidget *m_mainWindow;
    TreeModel * m_model;
    QMap <QString, QString> titleTestTypes;
    QMap <int, QString> buttonMap;
    int m_currentTab;
    bool m_skipTestMessage;
};

#endif // QTFRONT_H
