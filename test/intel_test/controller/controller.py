import subprocess, json, os
from kubernetes import client, config, watch
from multiprocessing import Process
from sriovfecnodeconfigs_watcher import sriovfecnodeconfigs_watcher
import logging

logging.basicConfig(
    level=logging.INFO,
    filename=os.environ["LOG_DIRECTORY"] + "/controller.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def controller():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    old_spec = {}
    # Create the accelclusterconfig crd and start watching sriovfecnodeconfigs
    create_crd_and_start_watcher()
    # Update ham operationalstate to ENABLED
    update_hamconfig()
    # Watch for changes in spec
    w = watch.Watch()
    for event in w.stream(COApi.list_namespaced_custom_object, group, version, namespace, plural):
        event_object = event['object']
        new_spec = event_object.get('spec', {})
        status = event_object.get('status', {})
        updateStatus = True
        # See if there is difference in spec
        if new_spec != old_spec:
            # Now status of the crd is just updated according to the spec, however updating different parts of the spec could trigger different operations in the HAM
            match new_spec.get("accelOperation", ""):
                case "STARTAALLPU":
                    new_status = start_aal_lpu(new_spec, status)
                case "STOPAALLPU":
                    new_status = stop_aal_lpu(new_spec, status)
                case "SETAALACCELCONFIG":
                    config_update(new_spec, status, COApi)
                    updateStatus = False
                case "SETAALACCELIDENTIFIER":
                    new_status = identifier_update(new_spec, status)
                case _:
                    updateStatus = False
            if updateStatus:
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
    hwAccelId = new_spec.get("hwAccelId", "")
    lpuId = new_spec.get("aalLpuId", "")
    # Backend commands to actually stop AAL-LPU
    accelDevices = status.get("hwAccelList", [])
    for accelDevice in accelDevices:
        if accelDevice.get("hwAccelId","") == hwAccelId:
            for lpu in accelDevice.get("aalLpu", []):
                if lpu.get("aalLpuId","") == lpuId:
                    lpu["status"] = "STARTED"
    return status
    
def stop_aal_lpu(new_spec, status):
    hwAccelId = new_spec.get("hwAccelId", "")
    lpuId = new_spec.get("aalLpuId", "")
    # Backend commands to actually stop AAL-LPU
    accelDevices = status.get("hwAccelList", [])
    for accelDevice in accelDevices:
        if accelDevice.get("hwAccelId","") == hwAccelId:
            for lpu in accelDevice.get("aalLpu", []):
                if lpu.get("aalLpuId","") == lpuId:
                    lpu["status"] = "STOPPED"
    return status

def config_update(new_spec, status, COApi):
    config = new_spec.get("configuration", {})
    sriovCrdGroup = "sriovfec.intel.com"
    sriovCrdVersion = "v2"
    sriovCrdNamespace = "vran-acceleration-operators"
    sriovCrdPlural = "sriovfecclusterconfigs"
    hwAccelConfigList = config.get("hwAccelList", [])
    # TODO: Delete old config if there is one for the node
    try:
        for hwAccelConfig in hwAccelConfigList:
            body = {
                "apiVersion": f"{sriovCrdGroup}/{sriovCrdVersion}",
                "kind": "SriovFecClusterConfig",
                "priority": 1,
                "metadata": {
                    "name": "config",
                    "namespace": sriovCrdNamespace
                },
                "spec": {
                    "drainSkip": True,
                    "acceleratorSelector": {
                        "pciAddress": hwAccelConfig.get("extensions", [])[0].get("pciAddress", {})
                    },
                    "nodeSelector": {
                        "kubernetes.io/hostname": hwAccelConfig.get("extensions", [])[0].get("node", {})
                    },
                    "physicalFunction": {
                        "bbDevConfig": hwAccelConfig.get("extensions", [])[0].get("bbDevConfig", {}),
                        "pfDriver": hwAccelConfig.get("imageLocation", ""),
                        "vfAmount": hwAccelConfig.get("numAalLpusConfigured", None),
                        "vfDriver": hwAccelConfig.get("aalLpu", [])[0].get("imageLocation", ""), # All lpus use same image
                    }
                }
            }
            COApi.create_namespaced_custom_object(sriovCrdGroup, sriovCrdVersion, sriovCrdNamespace, sriovCrdPlural, body)
            logging.info(f"Config custom resource created")
    except Exception as e:
        logging.error(f"Could not update configuration: {e}")

def identifier_update(new_spec, status):
    hwAccelId = new_spec.get("hwAccelId", "")
    vendorName = new_spec.get("vendorName", "")
    model = new_spec.get("model", "")
    serialNumber = new_spec.get("serialNum", "")
    accelDevices = status.get("hwAccelList", [])
    accelIndex = get_accel_index_in_status(accelDevices, vendorName, model, serialNumber)
    if accelIndex >= 0:
        status["hwAccelList"][accelIndex]["hwAccelId"] = hwAccelId
    return status

# If index < 0, accel not found
def get_accel_index_in_status(accelDevices, vendorName, model, serialNumber):
    index = -1
    for i in range(len(accelDevices)):
        if accelDevices[i].get('serialNum', "") == serialNumber and accelDevices[i].get('vendorName', "") == vendorName and accelDevices[i].get('model', "") == model:
            index = i
    return index

def create_crd_and_start_watcher():

    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    accelCrdGroup = os.environ["ACCELCRD_GROUP"]
    accelCrdVersion = os.environ["ACCELCRD_VERSION"]
    accelCrdNamespace = os.environ["ACCELCRD_NAMESPACE"]
    accelCrdPlural = os.environ["ACCELCRD_NAME_PLURAL"]
    accelCrdName = os.environ["ACCELCRD_NAME"]
    accelCrdKind = os.environ["ACCELCRD_KIND"]

    body = {
        "apiVersion": f"{accelCrdGroup}/{accelCrdVersion}",
        "kind": accelCrdKind,
        "priority": 1,
        "metadata": {
            "name": accelCrdName,
            "namespace": accelCrdNamespace
        },
        "spec": {
            "accelOperation": None,
            "configuration": {
                "hwAccelList": []
            }
        }
    }
    COApi.create_namespaced_custom_object(accelCrdGroup, accelCrdVersion, accelCrdNamespace, accelCrdPlural, body)

    p1 = Process(target=sriovfecnodeconfigs_watcher)
    p1.start()

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