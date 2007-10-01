import re

import xml.dom.minidom

# HAL Specific

def createDevice(document, parent_element, id, udi, parent=None):
    device = document.xml.createElement('device')
    device.setAttribute('id', str(id))
    device.setAttribute('udi', str(udi))
    if parent:
        device.setAttribute('parent', str(parent))

    parent_element.appendChild(device)

    return device

def createProperty(document, parent, name=None, value=None):
    property = createTypedElement(document, 'property', parent, name, value)
    parent.appendChild(property)
    return property

# Generic

def getType(source):
    # Convert the type to a string, find the start and end, then slice it.
    source_type = str(type(source))

    start = source_type.index("'") + 1
    end = source_type.rindex("'")

    result = source_type[start:end]

    return result 

def createElement(document, name, parent=None, value=None):
    element = document.xml.createElement(str(name))
    if parent:
        parent.appendChild(element)

    if value:
        element_value = document.xml.createTextNode(str(value))
        element.appendChild(element_value)

    return element

def createTypedElement(document, element_name, parent=None, name=None,
                       value=None, hide_type=False, child_name='property'):
    element = document.xml.createElement(str(element_name))

    if parent:
        parent.appendChild(element)

    if name:
        element.setAttribute('name', str(name))

    if value:
        value_type = getType(value)

        if not hide_type:
            element.setAttribute('type', str(value_type))

        if re.match('(list|dbus\.Array)', value_type):
            for v in value:
                createTypedElement(document, child_name, element,  None, v)
        elif re.match('(dict|dbus\.Dictionary)', value_type):
            for k in value.keys():
                createTypedElement(document, child_name, element, k,
                                   value[k])
        else:
            element_value = document.xml.createTextNode(str(value))
            element.appendChild(element_value)

    return element
