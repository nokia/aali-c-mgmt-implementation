import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from utils import accel_cr_mapping

def set_aal_accel_identifier(vendor_name: str, model: str, serial_number: str, hw_accel_id: str):
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    # Needed for json-patch
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    try:
        spec = {
                "accelOperation": "SETAALACCELIDENTIFIER",
                "hwAccelId": hw_accel_id,
                "vendorName": vendor_name,
                "model": model,
                "serialNum": serial_number
            }
        body = [{"op": "add", "path": "/spec", "value": spec}]
        COApi.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
        return {
            "status_of_operation": "success"
            }
    except ApiException as e:
        print("Exception when trying to get interface service: %s\n" % e)

    return {
        "status_of_operation": "failure"
        }
# If index < 0, accel not found
def get_accel_index_in_spec(accel_devices: list, vendor_name: str, model: str, serial_number: str):
    index = -1
    for i in range(len(accel_devices)):
        if accel_cr_mapping.get_hw_accel_serial_number(accel_devices[i]) == serial_number and accel_cr_mapping.get_hw_accel_vendor_name(accel_devices[i]) == vendor_name and accel_cr_mapping.get_hw_accel_model(accel_devices[i]) == model:
            index = i
    return index

if __name__ == "__main__":
    print(set_aal_accel_identifier())