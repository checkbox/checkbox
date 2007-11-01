distribution_source = "/etc/lsb-release"
distribution_release_keys = {"DISTRIB_ID": "distributor-id",
                             "DISTRIB_DESCRIPTION": "description",
                             "DISTRIB_RELEASE": "release",
                             "DISTRIB_CODENAME": "codename"}

distribution_properties = {}


def get_distribution():
    if not distribution_properties:
        fd = file(distribution_source, "r")
        for line in fd.readlines():
            key, value = line.split("=")
            if key in distribution_release_keys:
                key = distribution_release_keys[key.strip()]
                value = value.strip().strip('"')
                distribution_properties[key] = value

    return distribution_properties
