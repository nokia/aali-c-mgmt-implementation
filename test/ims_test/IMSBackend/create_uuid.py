import uuid

def create_uuid(vendorID, deviceID, serialNumber):

    input = vendorID + "-" + deviceID + "-" + serialNumber
    new_uuid = uuid.uuid5(uuid.NAMESPACE_URL, input)

    return new_uuid