import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def get_accel_cr_status():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]

    try:
        api_response = COApi.get_namespaced_custom_object_status(group, version, namespace, plural, name)
        return api_response.get("status", {})
    except ApiException as e:
        print("Exception when trying to get accel custom resource status: %s\n" % e)
    
    return {}
