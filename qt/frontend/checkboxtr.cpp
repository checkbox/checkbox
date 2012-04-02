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
// Self
#include <checkboxtr.h>

// Qt

// libc
#include <libintl.h>

void trInit(const char* domain, const char* localeDir)
{
    setlocale(LC_ALL, "");
    bindtextdomain(domain, localeDir);
    textdomain(domain);
}

QString checkboxTr(const char* text, const char* domain)
{
    return QString::fromUtf8(dgettext(domain, text));
}

QString checkboxTr(const char* singular, const char* plural, int n, const char* domain)
{
    QString text = QString::fromUtf8(dngettext(domain, singular, plural, n));
    // Note: if `text` is "%%n" (meaning the string on screen should be "%n"
    // literally), this will fail. I think we don't care for now.
    text.replace("%n", QString::number(n));
    return text;
}
