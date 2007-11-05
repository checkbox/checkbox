import md5

from hwtest.device import DeviceManager


system_id = None


def get_system_id():
    global system_id
    if not system_id:
        device_manager = DeviceManager()
        computer = device_manager.get_device_by_udi("/org/freedesktop/Hal/devices/computer")

        fingerprint = md5.new()
        fingerprint.update(computer.properties["system.vendor"])
        fingerprint.update(computer.properties["system.product"])
        system_id = fingerprint.hexdigest()

    return system_id
