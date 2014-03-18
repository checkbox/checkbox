#include <QDebug>
#include <QStringList>
#include "settings.h"

Settings::Settings(QObject *parent) : QObject(parent)
{
    m_settings = new QSettings();
}

Settings::Settings(const QString &fileName, QObject *parent) : QObject(parent)
{
    m_settings = new QSettings(fileName, QSettings::NativeFormat);
}

void Settings::setValue(const QString &key, const QVariant &value) {
    m_settings->setValue(key, value);
}

QString Settings::value(const QString &key, const QString &defaultValue) const {
    return m_settings->value(key, defaultValue).toStringList().at(0);
}

Settings::~Settings()
{
  delete m_settings;
}
