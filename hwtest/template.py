import os
import re
import locale
import logging

from os import environ


class Template(object):

    def __init__(self, filename_field=None, unique_fields=[]):
        self._filename_field = filename_field
        self._unique_fields = unique_fields

        self._languages = self._get_languages()

    def _add_modifier(self, locale, modifier):
        return "%s.%s" % (locale, modifier)

    def _add_territory(self, locale, territory):
        return re.sub(r"([^_@.]+)", "\\1%s" % territory, locale)

    def _add_charset(self, locale, charset):
        return re.sub(r"([^@.]+)", "\\1%s" % charset, locale)

    def _merge_lists(self, primaries, secondaries):
        for primary, secondary in zip(primaries, secondaries):
            yield primary
            yield secondary

    def _get_locale_list(self, locale):
        regex = re.compile(r"(@[^.]+)")
        modifier_match = regex.search(locale)
        locale = regex.sub("", locale)

        locale_match = re.match(r"([^_@.]+)(_[^_@.]+)?(\..+)?", locale)
        if not locale_match:
            raise Exception, "Unknown locale format: %s" % locale

        ret = [locale_match.group(1)]
        if modifier_match:
            modifier = modifier_match.group(1)
            modifiers = [self._add_modifier(r, modifier) for r in ret]
            ret = self._merge_lists(modifiers, ret)

        if locale_match.group(2):
            territory = locale_match.group(2)
            territories = [self._add_territory(r, territory) for r in ret]
            ret = self._merge_lists(territories, ret)

        if locale_match.group(3):
            charset = locale_match.group(3)
            charsets = [self._add_charset(r, charset) for r in ret]
            ret = self._merge_lists(charsets, ret)

        return ret

    def _get_languages(self):
        languages = []
        if environ.has_key("LANGUAGE") and environ["LANGUAGE"]:
            for language in environ["LANGUAGE"].split(":"):
                languages.extend(self._get_locale_list(language))

        language = locale.setlocale(locale.LC_MESSAGES)
        languages.extend(self._get_locale_list(language))

        return [l.lower() for l in languages]

    def _filter_languages(self, element):
        filter = {}
        basekeys = {}
        for key in element.keys():
            basekey = re.sub(r"-.+$", "", key)
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
            elif not re.search(r"-c$", key):
                field = "%s-c" % key
                if field in element:
                    filter[key] = element[field]
                    continue

            if key in element:
                filter[key] = element[key]
                continue

            if re.search(r"-c$", key):
                field = re.sub(r"-c$", "", key)
                if field in element:
                    filter[key] = element[field]
                    continue

            raise Exception, "No language found for key: %s" % key

        return filter

    def _reader(self, fd, size=4096, delimiter="\n\n"):
        buffer = ""
        while True:
            lines = (buffer + fd.read(size)).split(delimiter)
            buffer = lines.pop(-1)
            if not lines:
                break
            for line in lines:
                yield line

        yield buffer

    def load_filename(self, filename):
        logging.info("Loading elements from filename: %s", filename)

        elements = []
        descriptor = file(filename, "r")
        for string in self._reader(descriptor):
            if not string:
                break

            element = {}

            def _save(field, value, extended):
                if value and extended:
                    raise Exception, \
                        "Template %s has both a value and an extended value." \
                            % filename
                extended = extended.rstrip("\n")
                if field:
                    if element.has_key(field):
                        raise Exception, \
                            "Template %s has a duplicate field '%s'" \
                            " with a new value '%s'." \
                                % (filename, field, value)
                    element[field] = value or extended

            string = string.strip("\n")
            field = value = extended = ""
            for line in string.split("\n"):
                line.strip()
                match = re.search(r"^([-_.A-Za-z0-9]*):\s?(.*)", line)
                if match:
                    _save(field, value, extended)
                    field = match.groups()[0].lower()
                    value = match.groups()[1].rstrip()
                    extended = ""
                    continue

                if re.search(r"^\s\.$", line):
                    extended += "\n\n"
                    continue

                match = re.search(r"^\s(\s+.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += "\n"

                    extended += bit + "\n"
                    continue

                match = re.search(r"^\s(.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += " "

                    extended += bit
                    continue

                raise Exception, "Template %s parse error at: %s" \
                    % (filename, line)

            _save(field, value, extended)

            # Sanity checks
            if self._filename_field:
                if self._filename_field in element:
                    raise Exception, \
                        "Template %s already contains filename field: %s" \
                        % (filename, self._filename_field)
                element[self._filename_field] = os.path.basename(filename)

            for unique_field in self._unique_fields:
                if [e for e in elements \
                   if e[unique_field] == element[unique_field]]:
                    raise Exception, \
                        "Template %s contains duplicate fields: %s" \
                        % (filename, unique_field)

            element = self._filter_languages(element)
            elements.append(element)

        return elements

    def load_directory(self, directory, blacklist=[], whitelist=[]):
        logging.info("Loading elements from directory: %s", directory)

        elements = []
        if whitelist:
            names = whitelist
        else:
            names = [n for n in os.listdir(directory) if n not in blacklist]

        names = [n for n in names if n.endswith(".txt")]

        for name in names:
            filename = os.path.join(directory, name)
            elements.extend(self.load_filename(filename))

        return elements

    def load_directories(self, directories, blacklist=[], whitelist=[]):
        elements = []
        for directory in directories:
            elements.extend(self.load_directory(directory, blacklist, whitelist))

        return elements
