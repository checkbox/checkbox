#include <QtDBus>
#include <QMessageBox>
#include <QVariantMap>
#include <QScrollBar>
#include <QMenu>
#include <QMetaType>
#include <QDBusMetaType>
#include <QWidgetAction>
#include <QCheckBox>

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
    connect(ui->continueButton, SIGNAL(clicked()), this, SLOT(onFullTestsClicked()));
    connect(ui->deselectAllButton, SIGNAL(clicked()), this, SLOT(onDeselectAllClicked()));
    connect(ui->selectAllButton, SIGNAL(clicked()), this, SLOT(onSelectAllClicked()));
    connect(ui->buttonStartTesting, SIGNAL(clicked()), this, SLOT(onStartTestsClicked()));
    connect(ui->testTestButton, SIGNAL(clicked()), this, SIGNAL(startTestClicked()));
    connect(ui->nextTestButton, SIGNAL(clicked()), this, SLOT(onNextTestClicked()));
    connect(ui->previousTestButton, SIGNAL(clicked()), this, SLOT(onPreviousTestClicked()));
    connect(ui->buttonSubmitResults, SIGNAL(clicked()), this, SLOT(onSubmitTestsClicked()));
    connect(ui->buttonViewResults, SIGNAL(clicked()), this, SLOT(onReviewTestsClicked()));
    connect(m_mainWindow, SIGNAL(closed()), this, SLOT(onClosedFrontend()));
    connect(ui->treeView, SIGNAL(collapsed(QModelIndex)), this, SLOT(onJobItemChanged(QModelIndex)));
    connect(ui->treeView, SIGNAL(expanded(QModelIndex)), this, SLOT(onJobItemChanged(QModelIndex)));
    connect(ui->treeView, SIGNAL(clicked(QModelIndex)), this,  SLOT(onTestSelectionChanged()));
    connect(this, SIGNAL(testSelectionChanged()), this,  SLOT(onTestSelectionChanged()));
    ui->continueButton->setFocus();
    ui->stepsFrame->setFixedHeight(0);
    ui->buttonSubmitResults->setEnabled(false);
    ui->submissionDataLineEdit->setEnabled(false);
    ui->buttonViewResults->setEnabled(false);
    ui->testsTab->setTabEnabled(ui->testsTab->indexOf(ui->testing), false);
    ui->submitToHexr->setVisible(false);

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
    m_titleTestTypes["__ethernet__"] = checkboxTr("Ethernet Device Test", 0);
    m_titleTestTypes["__wireless__"] = checkboxTr("Wireless Test", 0);
    m_titleTestTypes["__optical__"] = checkboxTr("Optical Test", 0);
    m_titleTestTypes["__expresscard__"] = checkboxTr("ExpressCard Test", 0);
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

void QtFront::onClosedFrontend() {
    emit closedFrontend(m_doneTesting);
}

void QtFront::onTestSelectionChanged(QModelIndex index) {
    if (m_model->item(index.row())->isEnabled()) {
        ui->selectAllButton->setEnabled(! m_model->allInStatus(Qt::Checked));
        ui->deselectAllButton->setEnabled(! m_model->allInStatus(Qt::Unchecked));
    }
}

void QtFront::onDeselectAllClicked() {
    if (currentState != TREE || !m_model)
        return;
    m_model->warn();
    m_model->selectAll(false);
    emit testSelectionChanged();    
}

void QtFront::onSelectAllClicked() {
    if (currentState != TREE || !m_model)
        return;
    m_model->selectAll();
    emit testSelectionChanged();
}

void QtFront::onPreviousTestClicked() {
    emit previousTestClicked();
    updateTestStatus(STATUS_UNINITIATED);
}

void QtFront::setInitialState() {
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

void QtFront::onNextTestClicked() {
    QString currentResult = getTestResult();
    QString currentStatus;
    if (!m_skipTestMessage && currentResult == "skip") {
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
    if (currentResult == "skip"){
        currentStatus = STATUS_UNTESTED;
    }
    else if (currentResult == "yes"){
        currentStatus = STATUS_PASS;
    }
    else if (currentResult == "no"){
        currentStatus = STATUS_FAIL;
    }
    updateTestStatus(STATUS_UNTESTED);
}

void QtFront::onFullTestsClicked() {
    ui->tabWidget->setCurrentIndex(1);
    emit fullTestsClicked();
}

void QtFront::onStartTestsClicked() {
    ui->buttonStartTesting->setEnabled(false);
    ui->selectAllButton->setEnabled(false);
    ui->deselectAllButton->setEnabled(false);
    m_model->setInteraction(false);
    emit startTestsClicked();
}

void QtFront::onSubmitTestsClicked() {
    ui->buttonSubmitResults->setEnabled(false);
    ui->submissionDataLineEdit->setEnabled(false);
    ui->submitToHexr->setEnabled(false);
    m_doneTesting = true;
    emit submitTestsClicked();
}

void QtFront::onReviewTestsClicked() {
    m_doneTesting = true;
    emit reviewTestsClicked();
}

void QtFront::showText(QString text) {
    if (currentState == WELCOME) {
        ui->tabWidget->setCurrentIndex(0);
        m_mainWindow->show();
        ui->welcomeTextBox->setPlainText(text);
    } else if (currentState == SUBMISSION) {
        ui->submissionLabel->setText(text);
    }
}

void QtFront::showError(QString primary_text,
                        QString secondary_text, 
                        QString detailed_text) {
    QMessageBox msgBox(QMessageBox::Critical, checkboxTr("Error", 0),
                       primary_text, QMessageBox::Ok, ui->tabWidget);
    msgBox.setInformativeText(secondary_text);
    msgBox.setDetailedText(detailed_text);
    msgBox.exec();
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

    
    if (text.contains(checkboxTr("Working", 0))) {
        this->showTestControls(false);
        ui->testTypeLabel->setVisible(false);
        ui->purposeLabel->setVisible(false);
        ui->stepsFrame->setVisible(false);
    }

}

void QtFront::stopProgressBar()
{
    ui->progressBar->setRange(0, 100);
    ui->progressBar->setVisible(false);
    ui->progressLabel->setVisible(false);
    ui->progressLabel->setText("");

}

void QtFront::showEntry(QString text, QString value, QString label, bool showSubmitToHexr)
{
    currentState = SUBMISSION;
    // Submission data requested, so move to the results screen and 
    // hide the "run" screen contents
    ui->submissionLabel->setText(text);
    ui->submissionDataLabel->setText(label);
    ui->testsTab->setCurrentIndex(2);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    ui->buttonSubmitResults->setEnabled(true);
    ui->submissionDataLineEdit->setEnabled(true);
    ui->submissionDataLineEdit->setText(value);
    ui->buttonViewResults->setEnabled(true);

    if (showSubmitToHexr) {
        ui->submitToHexr->setVisible(true);
    }

}

void QtFront::showTest(QString purpose, 
                       QString steps, 
                       QString verification, 
                       QString info, 
                       QString comment,
                       QString testStatus,
                       QString testType, 
                       QString testName, 
                       bool enableTestButton) {
    currentState = TESTING;
    m_currentTestName = testName;
    updateTestStatus(STATUS_INPROGRESS);
    ui->radioTestTab->setVisible(true);
    ui->nextPrevButtons->setVisible(true);
    this->showTestControls(true);
    ui->testTestButton->setEnabled(enableTestButton);
    ui->skipTestRadioButton->setChecked(true);
    ui->commentsTextEdit->setPlainText(comment);
    ui->testsTab->setTabEnabled(ui->testsTab->indexOf(ui->testing), true);
    ui->tabWidget->setCurrentIndex(1);

    if (testStatus == STATUS_PASS) {
        ui->yesTestRadioButton->setChecked(true);
    }
    if (testStatus == STATUS_FAIL) {
        ui->noTestRadioButton->setChecked(true);
    }

    ui->testTypeLabel->setVisible(true);
    ui->purposeLabel->setVisible(true);
    ui->stepsFrame->setVisible(true);

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

void QtFront::showTestControls(bool enableTestControls) {
    ui->nextPrevButtons->setEnabled(enableTestControls);
    ui->noTestRadioButton->setEnabled(enableTestControls);
    ui->skipTestRadioButton->setEnabled(enableTestControls);
    ui->testTestButton->setEnabled(enableTestControls);
    ui->yesTestRadioButton->setEnabled(enableTestControls);
    ui->commentsTextEdit->setEnabled(enableTestControls);
}

void QtFront::setTestResult(bool status) {
    if (status) {
        ui->yesTestRadioButton->setChecked(true);
    }
    else {
        ui->noTestRadioButton->setChecked(true);
    }
}

QString QtFront::getTestResult() {
    QString result = "skip";
    if (ui->yesTestRadioButton->isChecked()){
        result = "yes";
    }
    if (ui->noTestRadioButton->isChecked()) {
        result = "no";
    }
    return result;
}

void QtFront::updateTestStatus(QStandardItem *item, QStandardItem *statusItem, QString status) {
    int numRows = item->rowCount();
    int done = 0;
    int inprogress = 0;
    for(int i = 0; i < numRows; i++) {
        QStandardItem * childItem = item->child(i,1);
        if (childItem->hasChildren()) {
            updateTestStatus(childItem, statusItem, status);
        }
        if (childItem->data(Qt::UserRole).toString() == m_currentTestName && !status.isEmpty()) {
            childItem->setText(m_statusStrings[status]);
        }
        if (childItem->text() == m_statusStrings[STATUS_PASS]) {
            done++;
        } else if (childItem->text() == m_statusStrings[STATUS_INPROGRESS]) {
            inprogress++;
        }
    }
    if (done == item->rowCount() && done != 0) {
        statusItem->setText(m_statusStrings[STATUS_PASS]);
    } else if (inprogress != 0 || done != 0) {
        statusItem->setText(m_statusStrings[STATUS_INPROGRESS]);
    } else {
        statusItem->setText(m_statusStrings[STATUS_UNINITIATED]);
    }
}

void QtFront::updateTestStatus(QString status) {
    for (int i=0; i < m_model->rowCount(); i++) {
        updateTestStatus(m_model->item(i,0), m_model->item(i,1), status);
    }
}

void QtFront::updateAutoTestStatus(QString status, QString currentTest) {
    if (!currentTest.isEmpty()) {
        m_currentTestName = currentTest;
    }
    updateTestStatus(status);
}

void QtFront::buildTree(QVariantMap options, 
                        QVariantMap defaults, 
                        QString baseIndex, 
                        QStandardItem *parentItem) {
    int internalIndex = 1;
    while (true) {
        QString index = baseIndex + "." + QString::number(internalIndex);
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

            if (parentItem) {
                // for children nodes
                QList<QStandardItem *> itemList;
                itemList << item << testStatusItem;
                parentItem->appendRow(itemList);
                buildTree(options, defaults, index, item);
            } else {
                // for root nodes
                buildTree(options, defaults, index, item);
                QList<QStandardItem *> itemList;
                itemList << item << testStatusItem;
                m_model->appendRow(itemList);
            }
        }
        internalIndex++;
    }
}

void QtFront::showTree(QString text, 
                       QVariantMap options, 
                       QVariantMap defaults,
                       QString deselect_warning) {
    ui->selectionLabel->setText(text);
    currentState = TREE;
    ui->testsTab->setCurrentIndex(0);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    // build the model only once
    if (!this->m_model) {
        this->m_model = new TreeModel();
        this->m_model->setColumnCount(2);
        buildTree(options, defaults, "1");
        ui->treeView->setModel(m_model);
        ui->treeView->header()->setResizeMode(0, QHeaderView::Stretch);
        ui->treeView->setColumnWidth(1, 150);
    }
    this->m_model->deselect_warning = QString(deselect_warning);

    updateTestStatus("");
    ui->treeView->show();
    ui->buttonStartTesting->setEnabled(true);
    m_model->setInteraction(true);
    emit testSelectionChanged();
}

void QtFront::onJobItemChanged(QStandardItem *item, 
                               QString job, 
                               QModelIndex baseIndex) {
    if (item->hasChildren()) {
        int numRows = item->rowCount();
        for(int i=0; i< numRows; i++) {
            QStandardItem *childItem = item->child(i, 1);
            onJobItemChanged(childItem,job, baseIndex);
        }
    }
}

void QtFront::onJobItemChanged(QModelIndex index) {
    QString job = m_model->data(index).toString();
    int numRows = m_model->rowCount();
    for(int i=0; i< numRows; i++) {
        QStandardItem *item = m_model->item(i, 1);
        onJobItemChanged(item, job, index);
    }
}

void QtFront::showInfo(QString text, 
                       QStringList options, 
                       QString defaultoption) {
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

QString QtFront::getSubmissionData() {
    return ui->submissionDataLineEdit->text();
}

bool QtFront::getSubmitToHexr() {
    return ui->submitToHexr->isChecked();
}

void QtFront::buildTestsToRun(QStandardItem *item, 
                              QString baseIndex, 
                              QVariantMap &items) {
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

QVariantMap QtFront::getTestsToRun() {
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

QString QtFront::getTestComment() {
    return ui->commentsTextEdit->toPlainText();
}

QtFront::~QtFront() {
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
