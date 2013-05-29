/*
 * This file is part of checkbox - taken from unity-2d 
 *
 * Copyright 2012 Canonical Ltd.
 *
 * Authors:
 * - Daniel Manrique <roadmr@ubuntu.com> - Checkbox modifications 
 * - Aurélien Gâteau <aurelien.gateau@canonical.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 3.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
#ifndef CHECKBOXTR_H
#define CHECKBOXTR_H

#include <QObject>
class QString;

/**
 * Installs our gettext catalog
 */
void trInit(const char* domain, const char* localeDir);

/**
 * Translate the string text.
 *
 * If domain is NULL, the default domain name (set in init(…)) is used instead.
 */
QString checkboxTr(const char* text, const char* domain = NULL);

/**
 * Plural version of checkboxTr. Should be called like this:
 *
 * checkboxTr("%n file", "%n files", count, domain)
 */
QString checkboxTr(const char* singular, const char* plural, int n, const char* domain = NULL);

#endif /* CHECKBOXTR_H */
