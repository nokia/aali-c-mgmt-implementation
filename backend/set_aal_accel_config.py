import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from utils import accel_cr_mapping

def set_aal_accel_config(hw_accel_list: list[dict]):
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    return_data = {} 
    mapped_hw_accel_list = []
    for hw_accel in hw_accel_list:
        mapped_hw_accel_list.append(accel_cr_mapping.set_hw_accel_cr_mapping(hw_accel))
    
    spec = {
            "accelOperation": "SETAALACCELCONFIG",
            "configuration": {
                "hwAccelList": mapped_hw_accel_list
                }
        }
    body = [{"op": "add", "path": "/spec", "value": spec}]
    try:
        COApi.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
        return_data["status_of_operation"] = "success"
    except ApiException as e:
        print("Exception when trying to patch accel config: %s\n" % e)
        return_data["status_of_operation"] = "failure"
    return return_data
