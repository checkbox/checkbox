#include <QtDBus>
#include <QMessageBox>
#include <QVariantMap>
#include <QScrollBar>
#include <QMenu>
#include <QMetaType>
#include <QDBusMetaType>

#include "qtfront.h"
#include "treemodel.h"
#include "step.h"
#include "ui_qtfront.h"

typedef QMap<QString, QString> myQMap;

Q_DECLARE_METATYPE(myQMap)
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
    m_statusModel(new QStandardItemModel()),
    m_currentTab(1),
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
    connect(ui->testsTab, SIGNAL(currentChanged(int)), this, SLOT(onTabChanged(int)));
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

    m_titleTestTypes["__audio__"] = "Audio Test";
    m_titleTestTypes["__bluetooth__"] = "Bluetooth Test";
    m_titleTestTypes["__camera__"] = "Camera Test";
    m_titleTestTypes["__cpu__"] = "CPU Test";
    m_titleTestTypes["__disk__"] = "Disk Test";
    m_titleTestTypes["__firewire__"] = "Firewire Test";
    m_titleTestTypes["__graphics__"] = "Graphics Test";
    m_titleTestTypes["__info__"] = "Info Test";
    m_titleTestTypes["__input__"] = "Input Test";
    m_titleTestTypes["__keys__"] = "Keys Test";
    m_titleTestTypes["__mediacard__"] = "Media Card Test";
    m_titleTestTypes["__memory__"] = "Memory Test";
    m_titleTestTypes["__miscellanea__"] = "Miscellanea Test";
    m_titleTestTypes["__monitor__"] = "Monitor Test";
    m_titleTestTypes["__networking__"] = "Networking Test";
    m_titleTestTypes["__wireless__"] = "Wireless Test";
    m_titleTestTypes["__optical__"] = "Optical Test";
    m_titleTestTypes["__pcmcia-pcix__"] = "PCMCIA/PCIX Test";
    m_titleTestTypes["__power-management__"] = "Power Management Test";
    m_titleTestTypes["__suspend__"] = "Suspend Test";
    m_titleTestTypes["__usb__"] = "USB Test";

    m_statusStrings["uninitiated"] = tr("Not Started");
    m_statusStrings["pass"] = tr("Done");
    m_statusStrings["fail"] = tr("Done");
    m_statusStrings["unsupported"] = tr("Not Supported");
    m_statusStrings["unresolved"] = tr("Not Resolved");
    m_statusStrings["untested"] = tr("Not Tested");
    m_statusStrings["inprogress"] = tr("In Progress");

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
    QAction *selectAll = menu.addAction(tr("Select All"));
    QAction *deselectAll = menu.addAction(tr("Deselect All"));

    QAction* selectedItem = menu.exec(position);
    if (selectedItem && selectedItem == selectAll)
    {
        m_model->selectAll();
    } else if (selectedItem && selectedItem == deselectAll) {
        m_model->selectAll(false);
    }
}

void QtFront::onYesTestClicked() {
    emit yesTestClicked();
    updateTestStatus(m_statusStrings["pass"]);

}

void QtFront::onNoTestClicked() {
    emit noTestClicked();
    updateTestStatus(m_statusStrings["fail"]);
}

void QtFront::onPreviousTestClicked() {
    emit previousTestClicked();
    updateTestStatus(m_statusStrings["uninitiated"]);
}

void QtFront::setInitialState()
{
    currentState = WELCOME;
    m_skipTestMessage = false; 
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);
    ui->testsTab->setCurrentIndex(1);
    ui->tabWidget->setCurrentIndex(0);
    m_model->deleteLater();
    ui->treeView->setModel(0);
    m_model = 0;
    m_statusList.clear();
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
    updateTestStatus(m_statusStrings["untested"]);
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

void QtFront::showTest(QString purpose, QString steps, QString verification, QString info, QString testType, QString testName, bool enableTestButton)
{
    currentState = TESTING;
    m_currentTestName = testName;
    updateTestStatus(m_statusStrings["inprogress"]);
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
            childItem->setText(status);
        }
        if (childItem->text() == m_statusStrings["pass"]) {
            childItem->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
            done++;
        } else if (childItem->text() == m_statusStrings["inprogress"]) {
            childItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
            inprogress++;
        } else if (childItem->text() == m_statusStrings["uninitiated"]) {
            childItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
        }
    }
    if (done == item->rowCount() && done != 0) {
        item->setText(m_statusStrings["pass"]);
        item->setData(QVariant(Qt::Checked), Qt::CheckStateRole);
    } else if (inprogress != 0 || done != 0) {
        item->setText(m_statusStrings["inprogress"]);
        item->setData(QVariant(Qt::PartiallyChecked), Qt::CheckStateRole);
    } else {
        item->setText(m_statusStrings["uninitiated"]);
        item->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);
    }
}

void QtFront::updateTestStatus(QString status) {
    for (int i=0; i < m_statusModel->rowCount(); i++) {
        updateTestStatus(m_statusModel->item(i,0), status);
    }
}

void QtFront::buildTree(QVariantMap options, QString baseIndex, QStandardItem *parentItem, QStandardItem *parentStatusItem)
{
    int internalIndex = 1;
    while (true) {
        QString index = baseIndex+"."+QString::number(internalIndex);
        QVariant value = options.value(index);
        QDBusArgument arg = value.value<QDBusArgument>();
        QMap<QString, QString> items = qdbus_cast<QMap<QString, QString> >(arg);
        if (items.isEmpty()) {
            break;
        } else {
            QString test = items.keys().at(0);
            QString status = items.values().at(0);
            QStandardItem *item = new QStandardItem(test);
            QStandardItem *testStatusItem = new QStandardItem(m_statusStrings[status]);

            item->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled| Qt::ItemIsTristate);
            item->setData(QVariant(Qt::Checked), Qt::CheckStateRole);

            testStatusItem->setData(test, Qt::UserRole);
            testStatusItem->setFlags(Qt::ItemIsUserCheckable | Qt::ItemIsEnabled|Qt::ItemIsTristate);
            testStatusItem->setData(QVariant(Qt::Unchecked), Qt::CheckStateRole);

            if (parentItem) {
                // for children nodes
                parentItem->appendRow(item);
                parentStatusItem->appendRow(testStatusItem);
                buildTree(options, index, item, testStatusItem);
            } else {
                // for root nodes
                buildTree(options, index, item, testStatusItem);
                m_model->appendRow(item);
                m_statusModel->appendRow(testStatusItem);
            }
        }
        internalIndex++;
    }
}

void QtFront::showTree(QString text, QVariantMap options)
{
    Q_UNUSED(text);
    currentState = TREE;
    ui->testsTab->setCurrentIndex(1);
    ui->radioTestTab->setVisible(false);
    ui->nextPrevButtons->setVisible(false);

    // build the model only once
    if (!this->m_model) {
        this->m_model = new TreeModel();
        buildTree(options, "1");
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
