#include "treemodel.h"
#include <QDebug>
#include <QErrorMessage>
TreeModel::TreeModel() : m_messageBox(0) 
{

}

void TreeModel::warn()
{
    if (!this->m_messageBox)
        this->m_messageBox = new QErrorMessage();
    this->m_messageBox->showMessage("Changeme: If you deselect this, the result wont be submitted to Ubuntu Friendly!");
}

bool TreeModel::setData(const QModelIndex &index, const QVariant &value, int role)
{
    qDebug() << index << value << role;
        QStandardItem *item = QStandardItemModel::itemFromIndex(index);
        if(!item)
            return false;

        warn();
        if (item->parent()) {
            qDebug() << "has parent";
            QStandardItemModel::setData(item->index(), value, role);
            // we are a child, and we have to update parent's status
            int selected = 0;
            for(int i=0; i< item->parent()->rowCount(); i++) {
                QStandardItem *childItem = item->parent()->child(i);
                if (childItem->checkState() == Qt::Checked) {
                    selected++;
                }
            }
            qDebug() << "selected" << selected;
            qDebug() << "rowCount" << item->parent()->rowCount();
            if (selected == item->parent()->rowCount()) {
                item->parent()->setCheckState(Qt::Checked);
            } else if (selected == 0) {
                item->parent()->setCheckState(Qt::Unchecked);
            } else {
                item->parent()->setCheckState(Qt::PartiallyChecked);
            }
        } else {
            // if we dont have a parent, then we are root. Deselect/select children
            for(int i=0; i< item->rowCount(); i++) {
                QStandardItem *childItem = item->child(i);
                QStandardItemModel::setData(childItem->index(), value, role);
            }
        }
        return QStandardItemModel::setData(index, value, role);
}

void TreeModel::setInteraction(bool value)
{
    for(int i=0; i< rowCount(); i++) {
        QStandardItem  *item = this->item(i, 0);
        if(!item)
            continue;
        item->setEnabled(value);
        for(int j=0; j< item->rowCount(); j++) {
            QStandardItem *childItem = item->child(j);
            if(!childItem)
                continue;
            childItem->setEnabled(value);
        }
    }
}
