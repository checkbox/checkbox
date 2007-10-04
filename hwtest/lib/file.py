def reader(fd, size=4096, delimiter="\n\n"):
    buffer = ''
    while True:
        lines = (buffer + fd.read(size)).split(delimiter)
        buffer = lines.pop(-1)
        if not lines:
            break
        for line in lines:
            yield line

    yield buffer
