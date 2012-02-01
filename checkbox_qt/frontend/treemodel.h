#ifndef TREEMODEL_H
#define TREEMODEL_H

#include <QStandardItemModel>

class TreeModel : public QStandardItemModel
{
public:
    TreeModel();
    bool setData(const QModelIndex &index, const QVariant &value, int role = Qt::EditRole);
    void setInteraction(bool value);
};

#endif // TREEMODEL_H
