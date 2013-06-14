#ifndef TREEMODEL_H
#define TREEMODEL_H

#include <QStandardItemModel>
#include <QErrorMessage>

class TreeModel : public QStandardItemModel
{
public:
    TreeModel();
    void warn();
    bool setData(const QModelIndex &index, const QVariant &value, int role = Qt::EditRole);
    void setInteraction(bool value);
    void selectAll(bool select = true);
    void changeAllChildren(QStandardItem *item, const QVariant &value, int role);
    void enableAllChildren(bool enable, QStandardItem *item);
    bool allInStatus(Qt::CheckState wanted_status);
    QErrorMessage *m_messageBox;
    QString deselect_warning;
};

#endif // TREEMODEL_H
