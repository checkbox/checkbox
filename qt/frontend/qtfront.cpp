#include <QtDBus>
#include <QMessageBox>
#include <QVariantMap>
#include <QScrollBar>
#include <QMenu>
#include <QMetaType>
#include <QDBusMetaType>
#include <QWidgetAction>

#include "qtfront.h"
#include "treemodel.h"
#include "step.h"
#include "ui_qtfront.h"

typedef QMap<QString, QString> myQMap;

Q_DECLARE_METATYPE(myQMap)
Q_DECLARE_METATYPE(QVariantMap)

#define STATUS_UNINITIATED "uninitiated"
#define STATUS_FAIL "fail"
#define STATUS_PASS "pass"
#define STATUS_UNSUPPORTED "unsupported"
#define STATUS_UNRESOLVED "unresolved"
#define STATUS_UNTESTED "untested"
#define STATUS_INPROGRESS "inprogress"

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
    m_statusModel(new QStandardItemModel()),
    m_currentTextComment(new QTextEdit()),
    m_currentTab(0),
    m_skipTestMessage(false),
    isFirstTimeWelcome(true),
    m_doneTesting(false)
{
    m_mainWindow = (QWidget*)new CustomQWidget();
    ui->setupUi(m_mainWindow);
    m_mainWindow->setWindowFlags(m_mainWindow->windowFlags()^Qt::WindowMaximizeButtonHint);

    CustomQTabWidget *tmpQTW = (CustomQTabWidget*)ui->tabWidget;
    tmpQTW->tabBar()->setVisible(false);
    tmpQTW = (CustomQTabWidget*) ui->radioTestTab;
    tmpQTW->tabBar()->setVisible(false);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    ui->treeView->verticalScrollBar()->setTracking(true);
    connect(ui->friendlyTestsButton, SIGNAL(clicked()), this, SLOT(onFullTestsClicked()));
    connect(ui->buttonStartTesting, SIGNAL(clicked()), this, SLOT(onStartTestsClicked()));
    connect(ui->testTestButton, SIGNAL(clicked()), this, SIGNAL(startTestClicked()));
    connect(ui->yesTestButton, SIGNAL(clicked()), this, SLOT(onYesTestClicked()));
    connect(ui->noTestButton, SIGNAL(clicked()), this, SLOT(onNoTestClicked()));
    connect(ui->nextTestButton, SIGNAL(clicked()), this, SLOT(onNextTestClicked()));
    connect(ui->previousTestButton, SIGNAL(clicked()), this, SLOT(onPreviousTestClicked()));
    connect(ui->buttonSubmitResults, SIGNAL(clicked()), this, SLOT(onSubmitTestsClicked()));
    connect(ui->buttonViewResults, SIGNAL(clicked()), this, SLOT(onReviewTestsClicked()));
    connect(m_mainWindow, SIGNAL(closed()), this, SLOT(onClosedFrontend()));
    connect(ui->checkBox, SIGNAL(toggled(bool)), SIGNAL(welcomeCheckboxToggled(bool)));
    connect(ui->treeView, SIGNAL(collapsed(QModelIndex)), this, SLOT(onJobItemChanged(QModelIndex)));
    connect(ui->treeView, SIGNAL(expanded(QModelIndex)), this, SLOT(onJobItemChanged(QModelIndex)));
    connect(ui->treeView->verticalScrollBar(), SIGNAL(valueChanged(int)), ui->statusView->verticalScrollBar(), SLOT(setValue(int)));
    ui->treeView->setContextMenuPolicy(Qt::CustomContextMenu);
    connect(ui->treeView, SIGNAL(customContextMenuRequested(const QPoint&)), this, SLOT(onSelectAllContextMenu(const QPoint&)));
    ui->stepsFrame->setFixedHeight(0);
    ui->buttonSubmitResults->setEnabled(false);
    ui->lineEditEmailAddress->setEnabled(false);
    ui->buttonViewResults->setEnabled(false);

    // comment box
    ui->commentTestButton->setMenu(new QMenu());
    QWidgetAction *action = new QWidgetAction(ui->commentTestButton);
    action->setDefaultWidget(m_currentTextComment);
    ui->commentTestButton->menu()->addAction(action);
    // force cursor blink without having to click inside the QTextEdit
    m_currentTextComment->setFocus();
    m_currentTextComment->setStyleSheet("background-color: white");

    m_titleTestTypes["__audio__"] = checkboxTr("Audio Test",0);
    m_titleTestTypes["__bluetooth__"] = checkboxTr("Bluetooth Test", 0);
    m_titleTestTypes["__camera__"] = checkboxTr("Camera Test", 0);
    m_titleTestTypes["__cpu__"] = checkboxTr("CPU Test", 0);
    m_titleTestTypes["__disk__"] = checkboxTr("Disk Test", 0);
    m_titleTestTypes["__firewire__"] = checkboxTr("Firewire Test", 0);
    m_titleTestTypes["__graphics__"] = checkboxTr("Graphics Test", 0);
    m_titleTestTypes["__info__"] = checkboxTr("Info Test", 0);
    m_titleTestTypes["__input__"] = checkboxTr("Input Test", 0);
    m_titleTestTypes["__keys__"] = checkboxTr("Keys Test", 0);
    m_titleTestTypes["__mediacard__"] = checkboxTr("Media Card Test", 0);
    m_titleTestTypes["__memory__"] = checkboxTr("Memory Test", 0);
    m_titleTestTypes["__miscellanea__"] = checkboxTr("Miscellanea Test", 0);
    m_titleTestTypes["__monitor__"] = checkboxTr("Monitor Test", 0);
    m_titleTestTypes["__networking__"] = checkboxTr("Networking Test", 0);
    m_titleTestTypes["__wireless__"] = checkboxTr("Wireless Test", 0);
    m_titleTestTypes["__optical__"] = checkboxTr("Optical Test", 0);
    m_titleTestTypes["__pcmcia-pcix__"] = checkboxTr("PCMCIA/PCIX Test", 0);
    m_titleTestTypes["__power-management__"] = checkboxTr("Power Management Test", 0);
    m_titleTestTypes["__suspend__"] = checkboxTr("Suspend Test", 0);
    m_titleTestTypes["__usb__"] = checkboxTr("USB Test", 0);

    m_statusStrings[STATUS_UNINITIATED] = checkboxTr("Not Started", 0);
    m_statusStrings[STATUS_PASS] = checkboxTr("Done", 0);
    m_statusStrings[STATUS_FAIL] = checkboxTr("Done", 0);
    m_statusStrings[STATUS_UNSUPPORTED] = checkboxTr("Not Supported", 0);
    m_statusStrings[STATUS_UNRESOLVED] = checkboxTr("Not Resolved", 0);
    m_statusStrings[STATUS_UNTESTED] = checkboxTr("Not Tested", 0);
    m_statusStrings[STATUS_INPROGRESS] = checkboxTr("In Progress", 0);

}

void QtFront::setUiFlags(QVariantMap flags)
{
    // process all ui flags
    QVariant checked = flags["show_welcome_message"];
    ui->checkBox->setChecked(checked.toBool());
}

void QtFront::onClosedFrontend()
{
    emit closedFrontend(m_doneTesting);
}

void QtFront::onSelectAllContextMenu(const QPoint& pos)
{
    if (currentState != TREE || !m_model)
        return;

    QPoint position = ui->treeView->mapToGlobal(pos);
    QMenu menu;
    QAction *selectAll = menu.addAction(checkboxTr("Select All", 0));
    QAction *deselectAll = menu.addAction(checkboxTr("Deselect All", 0));

    QAction* selectedItem = menu.exec(position);
    if (selectedItem && selectedItem == selectAll)
    {
        m_model->selectAll();
    } else if (selectedItem && selectedItem == deselectAll) {
        m_model->warn();
        m_model->selectAll(false);
    }
}

void QtFront::onYesTestClicked() {
    emit yesTestClicked();
    updateTestStatus(STATUS_PASS);
}

void QtFront::onNoTestClicked() {
    emit noTestClicked();
    updateTestStatus(STATUS_FAIL);
}

void QtFront::onPreviousTestClicked() {
    emit previousTestClicked();
    updateTestStatus(STATUS_UNINITIATED);
}

void QtFront::setInitialState()
{
    currentState = WELCOME;
    m_skipTestMessage = false; 
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    ui->testsTab->setCurrentIndex(0);
    ui->tabWidget->setCurrentIndex(0);
    m_model->deleteLater();
    ui->treeView->setModel(0);
    m_model = 0;
    m_statusList.clear();
}

void QtFront::onNextTestClicked()
{
    if (!m_skipTestMessage) {
        QMessageBox msgBox(QMessageBox::Question, checkboxTr("Are you sure?", 0), checkboxTr("Do you really want to skip this test?", 0), 0, ui->tabWidget);
        QCheckBox dontPrompt(checkboxTr("Don't ask me again", 0), &msgBox);
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
    updateTestStatus(STATUS_UNTESTED);
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
    m_doneTesting = true;
    emit submitTestsClicked();
}

void QtFront::onReviewTestsClicked()
{
    m_doneTesting = true;
    emit reviewTestsClicked();
}

void QtFront::showText(QString text)
{
    if (currentState == WELCOME) {
        if(isFirstTimeWelcome) {
            isFirstTimeWelcome = false;
            if (ui->checkBox->isChecked()) {
                QTimer::singleShot(100, this, SLOT(onFullTestsClicked()));
            }
        } else {
            ui->tabWidget->setCurrentIndex(0);
        }
        m_mainWindow->show();
        ui->welcomeTextBox->setPlainText(text);
    } else if (currentState == SUBMISSION) {
        ui->submissionLabel->setText(text);
    }
}

void QtFront::showError(QString text)
{
    QMessageBox::critical(ui->tabWidget, checkboxTr("Error", 0), text);
    emit errorBoxClosed();
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
    currentState = SUBMISSION;
    // Email address requested, so move to the results screen and hide the "run" screen contents
    ui->submissionLabel->setText(text);
    ui->testsTab->setCurrentIndex(2);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    ui->buttonSubmitResults->setEnabled(true);
    ui->lineEditEmailAddress->setEnabled(true);
    ui->buttonViewResults->setEnabled(true);

}

void QtFront::showTest(QString purpose, QString steps, QString verification, QString info, QString comment, QString testType, QString testName, bool enableTestButton)
{
    currentState = TESTING;
    m_currentTestName = testName;
    m_currentTextComment->setText(comment);
    updateTestStatus(STATUS_INPROGRESS);
    ui->radioTestTab->setVisible(true);
    ui->nextPrevButtons->setVisible(true);
    ui->testTestButton->setEnabled(enableTestButton);
    ui->tabWidget->setCurrentIndex(1);

    foreach(QObject *object, ui->stepsFrame->children())
        object->deleteLater();

    ui->stepsFrame->setFixedHeight(0);
    ui->stepsFrame->update();
    ui->testsTab->setCurrentIndex(1);
    QStringList stepsList = steps.trimmed().split("\n");

    QRegExp r("[0-9]+\\. (.*)");
    int index = 1;
    ui->testTypeLabel->setText(m_titleTestTypes[testType]);
    ui->purposeLabel->setText(purpose);
    foreach(QString line, stepsList) {
        if (line.isEmpty())
            continue;
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

    if (!info.isEmpty()) {
        Step *information = new Step(ui->stepsFrame, info);
        information->move(0, ui->stepsFrame->height());
        ui->stepsFrame->setFixedHeight(ui->stepsFrame->height() + information->height());
    }

    Step *question = new Step(ui->stepsFrame, verification, QString("?"));
    question->move(0, ui->stepsFrame->height());
    ui->stepsFrame->setFixedHeight(ui->stepsFrame->height() + question->height());

}

void QtFront::showTestControls(bool enableTestControls)
{
    ui->testTestButton->setEnabled(enableTestControls);
    ui->yesTestButton->setEnabled(enableTestControls);
    ui->noTestButton->setEnabled(enableTestControls);
    ui->nextPrevButtons->setEnabled(enableTestControls);
}

void QtFront::setFocusTestYesNo(bool status)
{
    if (status) {
        ui->noTestButton->setDefault(false);
        ui->noTestButton->clearFocus();
        ui->yesTestButton->setDefault(true);
        ui->yesTestButton->setFocus();
    }
    else {
        ui->yesTestButton->setDefault(false);
        ui->yesTestButton->clearFocus();
        ui->noTestButton->setDefault(true);
        ui->noTestButton->setFocus();
    }
}

void QtFront::updateTestStatus(QStandardItem *item, QString status)
{
    int numRows = item->rowCount();
    int done = 0;
    int inprogress = 0;
    for(int i=0; i< numRows; i++) {
        QStandardItem * childItem = item->child(i,0);
        if (childItem->hasChildren()) {
            updateTestStatus(childItem, status);
        }
        if (childItem->data(Qt::UserRole).toString() == m_currentTestName && !status.isEmpty()) {
            childItem->setText(m_statusStrings[status]);
        }
        if (childItem->text() == m_statusStrings[STATUS_PASS]) {
            childItem->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
            done++;
        } else if (childItem->text() == m_statusStrings[STATUS_INPROGRESS]) {
            childItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
            inprogress++;
        } else if (childItem->text() == m_statusStrings[STATUS_UNINITIATED]) {
            childItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
        }
    }
    if (done == item->rowCount() && done != 0) {
        item->setText(m_statusStrings[STATUS_PASS]);
        item->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
    } else if (inprogress != 0 || done != 0) {
        item->setText(m_statusStrings[STATUS_INPROGRESS]);
        item->setData(QVariant(Qt::PartiallyChecked), Qt::CheckStateRole);
    } else {
        item->setText(m_statusStrings[STATUS_UNINITIATED]);
        item->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
    }
}

void QtFront::updateTestStatus(QString status) {
    for (int i=0; i < m_statusModel->rowCount(); i++) {
        updateTestStatus(m_statusModel->item(i,0), status);
    }
}

void QtFront::updateAutoTestStatus(QString status, QString currentTest) {
    if (!currentTest.isEmpty()) {
        m_currentTestName = currentTest;
    }
    updateTestStatus(status);
}

void QtFront::buildTree(QVariantMap options, QVariantMap defaults, QString baseIndex, QStandardItem *parentItem, QStandardItem *parentStatusItem)
{
    int internalIndex = 1;
    while (true) {
        QString index = baseIndex+"."+QString::number(internalIndex);
        QVariant value = options.value(index);
        QVariant defaultValue = defaults.value(index);
        QDBusArgument arg = value.value<QDBusArgument>();
        QDBusArgument defaultArg = defaultValue.value<QDBusArgument>();
        if (arg.currentSignature().isEmpty()) {
            break;
        }
        QMap<QString, QString> items = qdbus_cast<QMap<QString, QString> >(arg);
        QMap<QString, bool> defaultItems = qdbus_cast<QMap<QString, bool> >(defaultArg);
        if (items.isEmpty()) {
            break;
        } else {
            QString test = items.keys().at(0);
            QString status = items.values().at(0);
            bool active = defaultItems.values().at(0);
            QStandardItem *item = new QStandardItem(test);
            QStandardItem *testStatusItem = new QStandardItem(m_statusStrings[status]);

            item->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled| Qt::ItemIsTristate);
            if (active) {
                item->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
            } else {
                item->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
            }

            testStatusItem->setData(test, Qt::UserRole);
            testStatusItem->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled|Qt::ItemIsTristate);
            testStatusItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);

            if (parentItem) {
                // for children nodes
                parentItem->appendRow(item);
                parentStatusItem->appendRow(testStatusItem);
                buildTree(options, defaults, index, item, testStatusItem);
            } else {
                // for root nodes
                buildTree(options, defaults, index, item, testStatusItem);
                m_model->appendRow(item);
                m_statusModel->appendRow(testStatusItem);
            }
        }
        internalIndex++;
    }
}

void QtFront::showTree(QString text, QVariantMap options, QVariantMap defaults)
{
    Q_UNUSED(text);
    currentState = TREE;
    ui->testsTab->setCurrentIndex(0);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    // build the model only once
    if (!this->m_model) {
        this->m_model = new TreeModel();
        buildTree(options, defaults, "1");
        ui->treeView->setModel(m_model);
        ui->statusView->setModel(m_statusModel);
    }

    updateTestStatus("");
    ui->treeView->show();
    ui->buttonStartTesting->setEnabled(true);
    m_model->setInteraction(true);
}

void QtFront::onJobItemChanged(QStandardItem *item, QString job, QModelIndex baseIndex)
{
    if (item->hasChildren()) {
        int numRows = item->rowCount();
        for(int i=0; i< numRows; i++) {
            QStandardItem *childItem = item->child(i, 0);
            onJobItemChanged(childItem,job, baseIndex);
        }
    }
    if (item->data(Qt::UserRole) == job) {
        ui->statusView->setExpanded(item->index(), ui->treeView->isExpanded(baseIndex));
    }

}

void QtFront::onJobItemChanged(QModelIndex index)
{
    QString job = m_model->data(index).toString();
    int numRows = m_statusModel->rowCount();
    for(int i=0; i< numRows; i++) {
        QStandardItem *item = m_statusModel->item(i, 0);
        onJobItemChanged(item, job, index);
    }
}

void QtFront::showInfo(QString text, QStringList options, QString defaultoption)
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
    dialog->setWindowTitle(checkboxTr("Info", 0));
    dialog->exec();
    QString result = buttonMap[dialog->clickedButton()];
    delete dialog;
    emit infoBoxResult(result);
}

QString QtFront::getEmailAddress()
{
    return ui->lineEditEmailAddress->text();
}

void QtFront::buildTestsToRun(QStandardItem *item, QString baseIndex, QVariantMap &items)
{
    if (item->checkState() == Qt::Checked || item->checkState() == Qt::PartiallyChecked) {
        if (item->hasChildren()) {
            myQMap testMap;
            testMap[item->text()] = "menu";
            items[baseIndex] = QVariant::fromValue<QMap<QString,QString> >(testMap);
            int internalIndex = 1;
            for (int i = 0; i< item->rowCount(); i++) {
                QStandardItem *childItem = item->child(i);
                buildTestsToRun(childItem, baseIndex + "."+QString::number(internalIndex), items);
                if(childItem->checkState() == Qt::Checked || childItem->checkState() == Qt::PartiallyChecked)
                    internalIndex++;
            }
        } else {
            myQMap testMap;
            testMap[item->text()] = item->data(Qt::UserRole).toString();
            items[baseIndex] = QVariant::fromValue<QMap<QString,QString> > (testMap);
        }
    }
}

QVariantMap QtFront::getTestsToRun()
{
    QMap<QString, QVariant> selectedOptions;
    qDBusRegisterMetaType<QMap<QString, QString> >();
    int numRows = m_model->rowCount();
    int internalIndex = 1;
    for(int i=0; i< numRows; i++) {
        QStandardItem *item = m_model->item(i, 0);
        if (item->checkState() == Qt::Checked || item->checkState() == Qt::PartiallyChecked) {
            buildTestsToRun(item, "1." + QString::number(internalIndex), selectedOptions);
            internalIndex++;
        }
    }
    return selectedOptions;
}

QString QtFront::getTestComment()
{
    return m_currentTextComment->toPlainText();
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
