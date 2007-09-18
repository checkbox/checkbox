import os

def parse_pci_hex_string(name, string):
    return {name: int(string, 16)}

def parse_pci_class_string(name, string):
    class_int = int(string, 16)
    class_name = class_int >> 16
    subclass_name = (class_int >> 8) & 0xFF
    class_progif = class_int & 0xFF

    return {
        'class_name': class_name,
        'subclass_name': subclass_name,
        'class_progif': class_progif}

def parse_pci_name_string(name, string):
    domain = 0
    if string.count(':') == 2:
        (domain, bus, slot_function) = string.split(':')
    elif string.count(':') == 1:
        (bus, slot_function) = string.split(':')
    else:
        raise Exception, "%s: unknown pci string" % string

    (slot, function) = slot_function.split('.')
    return {
        'domain': int(domain, 16),
        'bus': int(bus, 16),
        'slot': int(slot, 16),
        'function': int(function, 16)}

def parse_pci_attribute_content(content):
    lines = content.split("\n")
    if len(lines) == 2 and not lines[1]:
        content = lines[0]
        content = content.strip()
    else:
        content = "\n".join(lines)

    return content

def read_pci_attribute_filename(filename):
    fd = file(filename, 'r')
    content = fd.read()
    fd.close()

    return parse_pci_attribute_content(content)

def walk_pci_device_directory(directory):
    device = {}
    pci_attributes_and_functions = {
        'class': parse_pci_class_string,
        'device': parse_pci_hex_string,
        'irq': parse_pci_hex_string,
        'subsystem_device': parse_pci_hex_string,
        'subsystem_vendor': parse_pci_hex_string,
        'vendor': parse_pci_hex_string}
    for pci_attribute, pci_function in pci_attributes_and_functions.items():
        filename = os.path.join(directory, pci_attribute)
        content = read_pci_attribute_filename(filename)
        device.update(pci_function(pci_attribute, content))

    return device

def walk_pci_devices_directory(directory):
    devices = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for dirname in dirnames:
            pci_device_directory = os.path.join(directory, dirname)
            device = walk_pci_device_directory(pci_device_directory)
            device.update(parse_pci_name_string('name', dirname))
            devices.append(device)

    return devices

def walk_pci_directory(directory):
    pci_devices_directory = os.path.join(directory, 'devices')
    return walk_pci_devices_directory(pci_devices_directory)

def get_pci_devices():
    pci_directory = os.path.join(os.sep, 'sys', 'bus', 'pci')
    return walk_pci_directory(pci_directory)

