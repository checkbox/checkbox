def parse_lines(lines):
    """Parse question lines and return the resulting list of
    dictionaries.

    Keyword arguments:
    lines -- lines containing a question
    """

    question = {}
    questions = []
    line_number = 0
    for line in lines:
        line_number += 1

        # Ignore comments
        if not line.startswith('#'):
            line = line.strip("\n")
            # Empty line is a dictionary separator
            if not line:
                if question:
                    questions.append(question)
                    question = {}
            # Starting space continues previous line
            elif line.startswith(' '):
                value = line.strip()
                if value:
                    if not question[key].endswith('\n\n'):
                        question[key] += ' '
                    question[key] += value
                else:
                    question[key] += '\n\n'
            # Otherwise, directory entry
            else:
                key, value = line.split(':', 1)
                value = value.strip()
                question[key] = value

    # Append last entry
    if question:
        questions.append(question)

    return questions

def parse_string(string):
    """Parse a question string and return the resulting list of
    dictionaries.

    Keyword arguments:
    string -- string containing a question
    """

    return parse_lines(string.split('\n'))

def parse_file(name):
    """Parse a question file and return the resulting list of
    dictionaries.

    Keyword arguments:
    name -- name of the question file
    """

    fd = file(name, 'r')
    questions = parse_lines(fd.readlines())
    fd.close()

    return questions

def parse_dir(name):
    """Parse a question directory and return the resulting list
    of dictionaries.

    Keyword arguments:
    name -- name of the question directory
    """

    # Iterate over each file in directory
    questions = []
    for root, dirnames, filenames in os.walk(name):
        for filename in filenames:
            if filename.endswith('.txt'):
                abs_filename = os.path.join(root, filename)
                questions.extend(parse_file(abs_filename))

    return questions
