#include <QtDBus>
#include <QMessageBox>
#include <QVariantMap>

#include "qtfront.h"
#include "treemodel.h"
#include "step.h"
#include "ui_qtfront.h"

Q_DECLARE_METATYPE(QVariantMap)

class CustomQTabWidget : QTabWidget
{
public:
    QTabBar* tabBar(){
        return QTabWidget::tabBar();
    }
};

QtFront::QtFront(QApplication *parent) :
    QDBusAbstractAdaptor(parent),
    currentState(WELCOME),
    ui(new Ui_main),
    m_model(0),
    m_currentTab(1),
    m_skipTestMessage(false)
{
    m_mainWindow = (QWidget*)new CustomQWidget();
    ui->setupUi(m_mainWindow);

    CustomQTabWidget *tmpQTW = (CustomQTabWidget*)ui->tabWidget;
    tmpQTW->tabBar()->setVisible(false);
    tmpQTW = (CustomQTabWidget*) ui->radioTestTab;
    tmpQTW->tabBar()->setVisible(false);
    connect(ui->testsTab, SIGNAL(currentChanged(int)), this, SLOT(onTabChanged(int)));
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    connect(ui->friendlyTestsButton, SIGNAL(clicked()), this, SLOT(onFullTestsClicked()));
    connect(ui->buttonStartTesting, SIGNAL(clicked()), this, SLOT(onStartTestsClicked()));
    connect(ui->testTestButton, SIGNAL(clicked()), this, SIGNAL(startTestClicked()));
    connect(ui->yesTestButton, SIGNAL(clicked()), this, SIGNAL(yesTestClicked()));
    connect(ui->noTestButton, SIGNAL(clicked()), this, SIGNAL(noTestClicked()));
    connect(ui->nextTestButton, SIGNAL(clicked()), this, SLOT(onNextTestClicked()));
    connect(ui->previousTestButton, SIGNAL(clicked()), this, SIGNAL(previousTestClicked()));
    connect(ui->buttonSubmitResults, SIGNAL(clicked()), this, SLOT(onSubmitTestsClicked()));
    connect(m_mainWindow, SIGNAL(closed()), this, SIGNAL(closedFrontend()));
    ui->stepsFrame->setFixedHeight(0);

    titleTestTypes["__audio__"] = "Audio Test";
    titleTestTypes["__bluetooth__"] = "Bluetooth Test";
    titleTestTypes["__camera__"] = "Camera Test";
    titleTestTypes["__cpu__"] = "CPU Test";
    titleTestTypes["__disk__"] = "Disk Test";
    titleTestTypes["__firewire__"] = "Firewire Test";
    titleTestTypes["__graphics__"] = "Graphics Test";
    titleTestTypes["__info__"] = "Info Test";
    titleTestTypes["__input__"] = "Input Test";
    titleTestTypes["__keys__"] = "Keys Test";
    titleTestTypes["__mediacard__"] = "Media Card Test";
    titleTestTypes["__memory__"] = "Memory Test";
    titleTestTypes["__miscellanea__"] = "Miscellanea Test";
    titleTestTypes["__monitor__"] = "Monitor Test";
    titleTestTypes["__networking__"] = "Networking Test";
    titleTestTypes["__wireless__"] = "Wireless Test";
    titleTestTypes["__optical__"] = "Optical Test";
    titleTestTypes["__pcmcia-pcix__"] = "PCMCIA/PCIX Test";
    titleTestTypes["__power-management__"] = "Power Management Test";
    titleTestTypes["__suspend__"] = "Suspend Test";
    titleTestTypes["__usb__"] = "USB Test";
    buttonMap[QMessageBox::Yes] = "yes";
    buttonMap[QMessageBox::No] = "no";

}

void QtFront::setInitialState()
{
    currentState = WELCOME;
    m_skipTestMessage = false; 
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    ui->testsTab->setCurrentIndex(1);
    ui->tabWidget->setCurrentIndex(0);
    this->m_model->deleteLater();
    ui->treeView->setModel(0);
    this->m_model = 0;
}

void QtFront::onNextTestClicked()
{
    if (!m_skipTestMessage) {
        QMessageBox msgBox(QMessageBox::Question, tr("Are you sure?"), tr("Do you really want to skip this test?"), 0, ui->tabWidget);
        QCheckBox dontPrompt(tr("Don't ask me again"), &msgBox);
        dontPrompt.blockSignals(true);
        msgBox.addButton(&dontPrompt, QMessageBox::ActionRole);
        QAbstractButton *yesButton = (QAbstractButton*)msgBox.addButton(QMessageBox::Yes);
        msgBox.addButton(QMessageBox::No);
        msgBox.exec();
        QAbstractButton *answerButton = msgBox.clickedButton(); 
        if ( dontPrompt.checkState() == Qt::Checked )
            m_skipTestMessage = true;
        if (yesButton == answerButton)
            emit nextTestClicked();
    } else {
        emit nextTestClicked();
    }
}

void QtFront::onTabChanged(int index)
{
    // check if the user asked to go back to the welcome screen
    if (index == 0) {
        if (currentState != TREE) {
            QMessageBox::StandardButton button = QMessageBox::question(ui->tabWidget, "Are you sure?", 
                    "This action will invalidate your tests, do you want to proceed?", 
                    QMessageBox::Yes|QMessageBox::No, QMessageBox::No);
            if(button == QMessageBox::Yes) {
                emit welcomeScreenRequested();
            } else {
                // user aborted, go back to the previous tab
                ui->testsTab->setCurrentIndex(m_currentTab);
            }
            return;
        } else {
            currentState = WELCOME;
            emit welcomeClicked();
        }
        return;
    }
    m_currentTab = index;
}

void QtFront::onFullTestsClicked()
{
    ui->tabWidget->setCurrentIndex(1);
    emit fullTestsClicked();
}

void QtFront::onStartTestsClicked()
{
    ui->buttonStartTesting->setEnabled(false);
    m_model->setInteraction(false);
    emit startTestsClicked();
}

void QtFront::onSubmitTestsClicked()
{
    ui->buttonSubmitResults->setEnabled(false);
    ui->lineEditEmailAddress->setEnabled(false);
    emit submitTestsClicked();
}

void QtFront::showText(QString text)
{
    if (currentState == WELCOME) {
        m_mainWindow->show();
        ui->tabWidget->setCurrentIndex(0);
        ui->welcomeTextBox->setPlainText(text);
    } else if (currentState == SUBMISSION) {
        ui->submissionWarningLabel->setText(text);
    }
}

void QtFront::showError(QString text)
{
    QMessageBox::critical(ui->tabWidget, "Error", text);
}

void QtFront::setWindowTitle(QString title)
{
    m_mainWindow->setWindowTitle(title);
}

void QtFront::startProgressBar(QString text)
{
    // if we are asked to display the progress, then 
    // go to the screen where the progress widget is shown
    ui->tabWidget->setCurrentIndex(1);
    ui->progressBar->setRange(0, 0);
    ui->progressBar->setVisible(true);
    ui->progressLabel->setVisible(true);
    ui->progressLabel->setText(text);

}

void QtFront::stopProgressBar()
{
    ui->progressBar->setRange(0, 100);
    ui->progressBar->setVisible(false);
    ui->progressLabel->setVisible(false);
    ui->progressLabel->setText("");

}

void QtFront::showEntry(QString text) 
{
    Q_UNUSED(text)
    currentState = SUBMISSION;
    // Email address requested, so move to the results screen and hide the "run" screen contents
    ui->testsTab->setCurrentIndex(3);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    ui->buttonSubmitResults->setEnabled(true);
    ui->lineEditEmailAddress->setEnabled(true);

}

void QtFront::showTest(QString purpose, QString steps, QString verification, QString info, QString testType, bool enableTestButton)
{
    currentState = TESTING;
    ui->radioTestTab->setVisible(true);
    ui->nextPrevButtons->setVisible(true);
    ui->testTestButton->setEnabled(enableTestButton);
    ui->tabWidget->setCurrentIndex(1);

    foreach(QObject *object, ui->stepsFrame->children())
        object->deleteLater();

    ui->stepsFrame->setFixedHeight(0);
    ui->stepsFrame->update();
    ui->testsTab->setCurrentIndex(2);
    QStringList stepsList = steps.trimmed().split("\n");

    qDebug() << "purpose" << purpose << "steps"<< stepsList  <<"verification" << verification;
    QRegExp r("[0-9]+\\. (.*)");
    int index = 1;
    ui->testTypeLabel->setText(titleTestTypes[testType]);
    ui->purposeLabel->setText(purpose);
    foreach(QString line, stepsList) {
        bool isInfo = true;
        QString step;
        if (r.indexIn(line.trimmed()) == 0) {
            isInfo = false;
            step = r.cap(1);
        } else {
            step = line;
        }

        Step *a;
        if (isInfo) {
            a = new Step(ui->stepsFrame, step);
        } else {
            a = new Step(ui->stepsFrame, step, QString::number(index));
            index++;
        }

        a->move(0, ui->stepsFrame->height());
        ui->stepsFrame->setFixedHeight(ui->stepsFrame->height() + a->height());
    }
    Step *question = new Step(ui->stepsFrame, verification, QString("?"));
    question->move(0, ui->stepsFrame->height());
    ui->stepsFrame->setFixedHeight(ui->stepsFrame->height() + question->height());

}

void QtFront::showTree(QString text, QMap<QString, QVariant > options)
{
    Q_UNUSED(text);
    currentState = TREE;
    ui->testsTab->setCurrentIndex(1);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    // build the model only once
    if (!this->m_model) {
        this->m_model = new TreeModel();

        QMapIterator<QString, QVariant> i(options);
        while (i.hasNext()) {
            i.next();
            QString section = i.key();
            QStandardItem *sectionItem = new QStandardItem(section);
            sectionItem->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled| Qt::ItemIsTristate);
            sectionItem->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
            QDBusArgument arg = i.value().value<QDBusArgument>();
            QMap<QString, QString> items = qdbus_cast<QMap<QString, QString> >(arg);
            QMapIterator<QString, QString> j(items);
            while (j.hasNext()) {
                j.next();
                QString test = j.key();
                if (test.isEmpty())
                    continue;
                QStandardItem *testItem = new QStandardItem(test);
                testItem->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled);
                testItem->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
                sectionItem->appendRow(testItem);
            }

            m_model->appendRow(sectionItem);
        }
        ui->treeView->setModel(m_model);
        ui->treeView->show();
    }
    ui->buttonStartTesting->setEnabled(true);
    m_model->setInteraction(true);
}

QString QtFront::showInfo(QString text, QStringList options, QString defaultoption)
{
    // workaround, show the main window if the welcome screen wasn't shown yet
    m_mainWindow->show();
    QMessageBox *dialog = new QMessageBox(ui->tabWidget);
    QMap<QAbstractButton*, QString> buttonMap;
    foreach(QString option, options) {
        QAbstractButton *connectButton = dialog->addButton(option, QMessageBox::AcceptRole);
        if (option == defaultoption)
            dialog->setDefaultButton((QPushButton*)connectButton);
        buttonMap[connectButton] = option;
    }
    dialog->setText(text);
    dialog->setWindowTitle("Info");
    dialog->exec();
    QString result = buttonMap[dialog->clickedButton()];
    delete dialog;
    return result;
}

QString QtFront::getEmailAddress()
{
    return ui->lineEditEmailAddress->text();
}

QVariantMap QtFront::getTestsToRun()
{
    QMap<QString, QVariant> selectedOptions;

    int numRows = m_model->rowCount();
    for(int i=0; i< numRows; i++) {
        QStandardItem *item = m_model->item(i, 0);
        QMap<QString, QVariant> itemDict;
        for(int j=0; j< item->rowCount(); j++) {
            if (item->child(j)->checkState() == Qt::Checked || item->child(j)->checkState() == Qt::PartiallyChecked) {
                itemDict[item->child(j)->text()] = QString("");
            }
        }

        if (item->checkState() == Qt::Checked || item->checkState() == Qt::PartiallyChecked) {
            selectedOptions[item->text()] = QVariant::fromValue<QVariantMap>(itemDict);
        }
    }

    return selectedOptions;
}

QtFront::~QtFront()
{
    delete ui;
}

bool QtFront::registerService() {
    QDBusConnection connection = QDBusConnection::sessionBus();
    if ( !connection.registerService("com.canonical.QtCheckbox") ) {
         qDebug() << "error registering service.";
         return false;
     }
     if ( !connection.registerObject("/QtFront", this) ) {
         qDebug() << "error registering object";
         return false;
     }

     return true;
}
