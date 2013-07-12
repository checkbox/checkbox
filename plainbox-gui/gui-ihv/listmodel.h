/*
 * Author: Christophe Dumez <dchris@gmail.com>
 * License: Public domain (No attribution required)
 * Website: http://cdumez.blogspot.com/
 * Version: 1.0
 */

#ifndef LISTMODEL_H
#define LISTMODEL_H

#include <QAbstractListModel>
#include <QList>
#include <QVariant>

class ListItem: public QObject {
  Q_OBJECT

public:
  ListItem(QObject* parent = 0) : QObject(parent) {}
  virtual ~ListItem() {}
  virtual QString id() const = 0;
  virtual QVariant data(int role) const = 0;
  virtual void setData(const QVariant & value, int role) = 0;
  virtual QHash<int, QByteArray> roleNames() const = 0;


signals:
  void dataChanged();
};

class ListModel : public QAbstractListModel
{
  Q_OBJECT
  Q_PROPERTY( int count READ getCount() NOTIFY countChanged())

signals:
    void countChanged();


public:
  explicit ListModel(ListItem* prototype, QObject* parent = 0);
  ~ListModel();
  int rowCount(const QModelIndex &parent = QModelIndex()) const;
  QVariant data(const QModelIndex &index, int role = Qt::DisplayRole) const;

  bool setData(const QModelIndex & index, const QVariant & value, int role = Qt::EditRole);
  Qt::ItemFlags flags(const QModelIndex &index) const;

  int getCount() { this->count = this->rowCount(); return count; }

  Q_INVOKABLE QVariant get(int row);
  Q_INVOKABLE void setProperty(int index, const QString& property, const QVariant& value);


  void appendRow(ListItem* item);
  void appendRows(const QList<ListItem*> &items);
  void insertRow(int row, ListItem* item);
  bool removeRow(int row, const QModelIndex &parent = QModelIndex());
  bool removeRows(int row, int count, const QModelIndex &parent = QModelIndex());
  ListItem* takeRow(int row);
  ListItem* find(const QString &id) const;
  QModelIndex indexFromItem( const ListItem* item) const;
  void clear();

protected:
    QHash<int, QByteArray> roleNames() const;


private slots:
  void handleItemChange();

private:
  ListItem* m_prototype;
  QList<ListItem*> m_list;
  int count;
};

#endif // LISTMODEL_H
