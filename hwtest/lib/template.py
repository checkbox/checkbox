from string import Template

def convert_string(string, substitutions):
    return Template(string).safe_substitute(substitutions)

def convert_file(source_file, destination_file, substitutions):
    source_value = file(source_file, 'r').read()

    destination_value = Template(source_value).safe_substitute(substitutions)
    file(destination_file, 'w').write(destination_value)
