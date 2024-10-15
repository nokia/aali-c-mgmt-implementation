import subprocess, json, os
from kubernetes import client, config, watch

def controller():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    # old_spec = COApi.get_namespaced_custom_object(group, version, namespace, plural, name).get('spec', {})
    old_spec = {}
    # Find accels in current cluster
    find_accels()
    # Update ham operationalstate to ENABLED
    update_hamconfig()
    # Watch for changes in spec
    w = watch.Watch()
    for event in w.stream(COApi.list_namespaced_custom_object, group, version, namespace, plural):
        event_object = event['object']
        new_spec = event_object.get('spec', {})
        status = event_object.get('status', {})
        operationFound = True
        # See if there is difference in spec
        if new_spec != old_spec:
            # Now status of the crd is just updated according to the spec, however updating different parts of the spec could trigger different operations in the HAM
            match new_spec.get("accelOperation", ""):
                case "STARTAALLPU":
                    new_status = start_aal_lpu(new_spec, status)
                case "STOPAALLPU":
                    new_status = stop_aal_lpu(new_spec, status)
                case "SETAALACCELCONFIG":
                    new_status = config_update(new_spec, status)
                case "SETAALACCELIDENTIFIER":
                    new_status = identifier_update(new_spec, status)
                case _:
                    operationFound = False
            if operationFound:
                data =  {
                    "apiVersion": event_object['apiVersion'],
                    "kind": event_object['kind'],
                    "metadata": {
                        "name": event_object['metadata']['name'],
                        "namespace": event_object['metadata']['namespace'],
                        "resourceVersion": event_object['metadata']['resourceVersion']
                    },
                    "status": new_status
                }
                COApi.patch_namespaced_custom_object_status(group, version, namespace, plural, name, data)
        old_spec = new_spec

def start_aal_lpu(new_spec, status):
    hw_accel_id = new_spec.get("hwAccelId", "")
    lpu_handle = new_spec.get("aalLpuHandle", "")
    # Backend commands to actually stop AAL-LPU
    accel_devices = status.get("hwAccelList", [])
    for accel_device in accel_devices:
        if accel_device.get("hwAccelId","") == hw_accel_id:
            for lpu in accel_device.get("aalLpu", []):
                if lpu.get("aalLpuHandle","") == lpu_handle:
                    lpu["status"] = "STARTED"
    return status
    
def stop_aal_lpu(new_spec, status):
    hw_accel_id = new_spec.get("hwAccelId", "")
    lpu_handle = new_spec.get("aalLpuHandle", "")
    # Backend commands to actually stop AAL-LPU
    accel_devices = status.get("hwAccelList", [])
    for accel_device in accel_devices:
        if accel_device.get("hwAccelId","") == hw_accel_id:
            for lpu in accel_device.get("aalLpu", []):
                if lpu.get("aalLpuHandle","") == lpu_handle:
                    lpu["status"] = "STOPPED"
    return status

def config_update(new_spec, status):
    config = new_spec.get("configuration", {})
    # Backend commands to actually apply configuration
    status.update(config)
    return status

def identifier_update(new_spec, status):
    hw_accel_id = new_spec.get("hwAccelId", "")
    vendor_name = new_spec.get("vendorName", "")
    model = new_spec.get("model", "")
    serial_number = new_spec.get("serialNum", "")
    accel_devices = status.get("hwAccelList", [])
    accelIndex = get_accel_index_in_status(accel_devices, vendor_name, model, serial_number)
    if accelIndex >= 0:
        status["hwAccelList"][accelIndex]["hwAccelId"] = hw_accel_id
    return status

# If index < 0, accel not found
def get_accel_index_in_status(accel_devices, vendor_name, model, serial_number):
    index = -1
    for i in range(len(accel_devices)):
        if accel_devices[i].get('serialNum', "") == serial_number and accel_devices[i].get('vendorName', "") == vendor_name and accel_devices[i].get('model', "") == model:
            index = i
    return index

def find_accels():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # For the test controller the crd will get mock values from file
    json_file_path = current_directory + "/hw_accel_list.json"
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    body = [{"op": "replace", "path": "/status", "value": data}]
    COApi.patch_namespaced_custom_object_status(group, version, namespace, plural, name, body)
    
def update_hamconfig():
    ham_crd_group = os.environ["HAMCRD_GROUP"]
    ham_crd_version = os.environ["HAMCRD_VERSION"]
    ham_crd_namespace = os.environ["HAMCRD_NAMESPACE"]
    ham_crd_plural = os.environ["HAMCRD_NAME_PLURAL"]
    ham_crd_name = os.environ["HAMCRD_NAME"]
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    body = [{"op": "replace", "path": "/status/aalHam/operationalState", "value": "ENABLED"}]
    COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)

if __name__ == "__main__":
    controller()