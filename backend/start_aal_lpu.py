import os
from kubernetes import client, config
from utils import accel_cr_mapping, get_accel_cr_status

def start_aal_lpu(hw_accel_id: str, lpu_handle: str):
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    # Needed for json-patch
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices_in_spec = accel_cr_mapping.get_hw_accel_list(accel_config_status)
    accel_index_in_spec = get_accel_index_in_spec(accel_devices_in_spec, hw_accel_id)

    if accel_index_in_spec >= 0:
        lpu_index_in_spec = get_lpu_index(accel_devices_in_spec[accel_index_in_spec], lpu_handle)
        if lpu_index_in_spec >= 0:
            spec = {
                    "accelOperation": "STARTAALLPU",
                    "hwAccelId": hw_accel_id,
                    "aalLpuHandle": lpu_handle
                }
            body = [{"op": "add", "path": "/spec", "value": spec}]
            COApi.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
            return {
                "status_of_operation": "success"
                }
    
    return {
        "status_of_operation": "failure"
        }

# If index < 0, accel not found
def get_accel_index_in_spec(accel_devices: list, hw_accel_id: str):
    index = -1
    for i in range(len(accel_devices)):
        if accel_cr_mapping.get_hw_accel_id(accel_devices[i]) == hw_accel_id:
            index = i
    return index

# If index < 0, lpu not found
def get_lpu_index(accel_device: list, lpu_handle: str):
    lpus = accel_cr_mapping.get_hw_accel_lpus(accel_device)
    index = -1
    for i in range(len(lpus)):
        if accel_cr_mapping.get_lpu_handle(lpus[i]) == lpu_handle:
            index = i
    return index

if __name__ == "__main__":
    print(start_aal_lpu())