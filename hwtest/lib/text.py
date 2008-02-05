def indent(text, count=1, step=2):
    """Intend each line of text by a given step.

    Keyword arguments:
    text -- text containing lines to indent
    count -- number of steps to indent (default 1)
    step -- number of spaces per indent (default 2)
    """

    indent = ' ' * step
    return "\n".join([indent * count + t for t in text.split("\n")])

def wrap(text, limit=72):
    """Wrap text into lines up to limit characters excluding newline.

    Keyword arguments:
    text -- text to wrap
    limit -- maximum number of characters per line (default 72)
    """

    lines = ['']
    if text:
        current = -1
        inside = False
        for line in text.split("\n"):
            words = line.split()
            if words:
                inside = True
                for word in words:
                    increment = len(word) + 1
                    if current + increment > limit:
                        current = -1
                        lines.append('')
                    current += increment
                    lines[-1] += word + ' '
            else:
                if inside:
                    inside = False
                    lines.append('')
                lines.append('')
                current = -1 

    return "\n".join(lines)
