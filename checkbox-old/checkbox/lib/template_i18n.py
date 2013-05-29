#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import re
import locale

from os import environ
from gettext import gettext as _

from checkbox.lib.template import Template


class TemplateI18n(Template):

    def __init__(self, *args, **kwargs):
        super(TemplateI18n, self).__init__(*args, **kwargs)

        self._languages = self._get_languages()

    def _add_modifier(self, language, modifier):
        return "%s.%s" % (language, modifier)

    def _add_territory(self, language, territory):
        return re.sub(r"([^_@.]+)", "\\1%s" % territory, language)

    def _add_charset(self, language, charset):
        return re.sub(r"([^@.]+)", "\\1%s" % charset, language)

    def _merge_lists(self, primaries, secondaries):
        for primary, secondary in zip(primaries, secondaries):
            yield primary
            yield secondary

    def _get_language_list(self, language):
        regex = re.compile(r"(@[^.]+)")
        modifier_match = regex.search(language)
        language = regex.sub("", language)

        language_match = re.match(r"([^_@.]+)(_[^_@.]+)?(\..+)?", language)
        if not language_match:
            raise Exception("Unknown language format: %s" % language)

        ret = [language_match.group(1)]
        if modifier_match:
            modifier = modifier_match.group(1)
            modifiers = [self._add_modifier(r, modifier) for r in ret]
            ret = self._merge_lists(modifiers, ret)

        if language_match.group(2):
            territory = language_match.group(2)
            territories = [self._add_territory(r, territory) for r in ret]
            ret = self._merge_lists(territories, ret)

        if language_match.group(3):
            charset = language_match.group(3)
            charsets = [self._add_charset(r, charset) for r in ret]
            ret = self._merge_lists(charsets, ret)

        return ret

    def _get_languages(self):
        languages = []
        if "LANGUAGE" in environ and environ["LANGUAGE"]:
            for language in environ["LANGUAGE"].split(":"):
                if language:
                    languages.extend(self._get_language_list(language))

        language = locale.setlocale(locale.LC_MESSAGES)
        languages.extend(self._get_language_list(language))

        return [l.lower() for l in languages]

    def _filter_field(self, field):
        lines = []
        separator = "\n\n"
        for line in field.split(separator):
            lines.append(_(line))

        return separator.join(lines)

    def _filter_languages(self, element):
        filter = {}
        basekeys = {}
        for key in element.keys():
            basekey = re.sub(r"^_?([^-]+).*$", "\\1", key)
            basekeys[basekey] = None

        for key in basekeys.keys():
            if self._languages:
                for language in self._languages:
                    field = "%s-%s" % (key, language)
                    if field in element:
                        filter[key] = element[field]
                        break
                if key in filter:
                    continue
            else:
                field = "%s-c" % key
                if field in element:
                    filter[key] = element[field]
                    continue

            if key in element:
                filter[key] = self._filter_field(element[key])
                continue
            else:
                field = "_%s" % key
                if field in element:
                    filter[key] = self._filter_field(element[field])
                    continue

            raise Exception("No language found for key: %s" % key)

        return filter

    def load_file(self, *args, **kwargs):
        elements = super(TemplateI18n, self).load_file(*args, **kwargs)

        return [self._filter_languages(e) for e in elements]
