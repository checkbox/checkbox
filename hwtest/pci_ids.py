PCI_IDS_FILE = '/usr/share/misc/pci.ids'
ID_NAME_SEP = '  '
SUB_ID_NAME_SEP = ' '
CLASS_PREFIX = 'C '

class PciIds:
    def __init__(self):
        fd = file(PCI_IDS_FILE, 'r')
        lines = fd.readlines()
        fd.close()

        (self.vendors, self.devices) = self._get_vendors_and_devices(lines)
        (self.classes, self.subclasses) = self._get_classes_and_subclasses(lines)

    def _get_vendors_and_devices(self, lines):
        vendor_id = 0
        vendors = {}
        devices = {}

        for line in lines:
            if line.startswith(CLASS_PREFIX):
                break

            line = line.rstrip()
            if not line.startswith('#') and line:
                if line.startswith('\t\t'):
                    # TODO
                    pass
                elif line.startswith('\t'):
                    line = line.lstrip()
                    (device_id, device_name) = line.split(ID_NAME_SEP, 1)
                    device_id = int(device_id, 16)
                    devices['%d.%d' % (vendor_id, device_id)] = device_name
                else:
                    (vendor_id, vendor_name) = line.split(ID_NAME_SEP, 1)
                    vendor_id = int(vendor_id, 16)
                    vendors[vendor_id] = vendor_name

        return (vendors, devices)

    def _get_classes_and_subclasses(self, lines):
        class_id = 0
        classes = {}
        subclasses = {}

        start_insert = False
        for line in lines:
            if line.startswith(CLASS_PREFIX):
                start_insert = True
            if not start_insert:
                continue

            line = line.rstrip()
            if not line.startswith('#') and line:
                if line.startswith('\t\t'):
                    # TODO
                    pass
                elif line.startswith('\t'):
                    line = line.lstrip()
                    (subclass_id, subclass_name) = line.split(ID_NAME_SEP, 1)
                    subclass_id = int(subclass_id, 16)
                    subclasses['%d.%d' % (class_id, subclass_id)] = subclass_name
                else:
                    (class_id, class_name) = line.split(ID_NAME_SEP, 1)
                    class_id = class_id.lstrip(CLASS_PREFIX)
                    class_id = int(class_id, 16)
                    classes[class_id] = class_name

        return (classes, subclasses)

    def get_vendor(self, vendor_id):
        return self.vendors[vendor_id]

    def get_device(self, vendor_id, device_id):
        return self.devices['%d.%d' % (vendor_id, device_id)]

    def get_class(self, class_id):
        return self.classes[class_id]

    def get_subclass(self, class_id, subclass_id):
        return self.subclasses['%d.%d' % (class_id, subclass_id)]

pci_ids = PciIds()

def get_vendor(vendor_id):
    return pci_ids.get_vendor(vendor_id)

def get_device(vendor_id, device_id):
    return pci_ids.get_device(vendor_id, device_id)

def get_class(class_id):
    return pci_ids.get_class(class_id)

def get_subclass(class_id, subclass_id):
    return pci_ids.get_subclass(class_id, subclass_id)
