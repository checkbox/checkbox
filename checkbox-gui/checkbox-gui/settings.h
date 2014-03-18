#ifndef SETTINGS_H
#define SETTINGS_H

#include <QObject>
#include <QSettings>

class Settings : public QObject
{
    Q_OBJECT

public:
    Settings(QObject *parent = 0);
    explicit Settings(const QString & filename, QObject *parent = 0);
    ~Settings();

public slots:
    void setValue(const QString & key, const QVariant & value);
    QString value(const QString &key, const QString &defaultValue = QString()) const;

private:
    QSettings* m_settings;
};

#endif // SETTINGS_H
