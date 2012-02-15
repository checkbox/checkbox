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
    QErrorMessage *m_messageBox;
};

#endif // TREEMODEL_H
