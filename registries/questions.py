import os
import re
import logging

from hwtest.lib.file import reader
from hwtest.lib.cache import cache

from hwtest.registry import Registry

from map import MapRegistry


class QuestionsRegistry(Registry):

    def _load_filename(self, filename):
        logging.info("Loading questions from filename: %s", filename)

        questions = []
        descriptor = file(filename, "r")
        for string in reader(descriptor):
            if not string:
                break

            question = {}
            question["suite"] = os.path.basename(filename)

            def _save(field, value, extended):
                if value and extended:
                    raise Exception, \
                        "Path %s has both a value and an extended value." \
                            % filename
                extended = extended.rstrip("\n")
                if field:
                    if question.has_key(field):
                        raise Exception, \
                            "Path %s has a duplicate field '%s'" \
                            " with a new value '%s'." \
                                % (filename, field, value)
                    question[field] = value or extended

            string = string.strip("\n")
            field = value = extended = ''
            for line in string.split("\n"):
                line.strip()
                match = re.search(r"^([-_.A-Za-z0-9]*):\s?(.*)", line)
                if match:
                    _save(field, value, extended)
                    field = match.groups()[0].lower()
                    value = match.groups()[1].rstrip()
                    extended = ''
                    basefield = re.sub(r"-.+$", "", field)
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

                raise Exception, "Path %s parse error at: %s" \
                    % (filename, line)

            _save(field, value, extended)

            if "name" not in question:
                raise Exception, \
                    "Question does not contain a 'name': %s" \
                        % question

            if [q for q in questions if q["name"] == question["name"]]:
                raise Exception, \
                    "Question %s already has a question of the same name." \
                        % question["name"]

            questions.append(question)

        return questions

    def _load_directory(self, directory):
        logging.info("Loading questions from directory: %s", directory)

        questions = []
        for name in [name for name in os.listdir(directory)
                     if name.endswith(".txt")]:
            filename = os.path.join(directory, name)
            questions.extend(self._load_filename(filename))

        return questions

    def _load_directories(self, directories):
        questions = []
        for directory in directories:
            questions.extend(self._load_directory(directory))

        return questions

    @cache
    def items(self):
        items = []
        directories = re.split("\s+", self.config.directories)
        questions = self._load_directories(directories)
        for question in questions:
            key = question["name"]
            value = MapRegistry(self.config, question)
            items.append((key, value))

        return items


factory = QuestionsRegistry
