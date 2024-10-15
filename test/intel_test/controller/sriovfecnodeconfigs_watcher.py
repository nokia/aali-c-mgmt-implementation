import json, requests, os, copy
from kubernetes import client, config, watch

def sriovfecnodeconfigs_watcher():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    accelCrdGroup = os.environ["ACCELCRD_GROUP"]
    accelCrdVersion = os.environ["ACCELCRD_VERSION"]
    accelCrdNamespace = os.environ["ACCELCRD_NAMESPACE"]
    accelCrdPlural = os.environ["ACCELCRD_NAME_PLURAL"]
    accelCrdName = os.environ["ACCELCRD_NAME"]
    sriovCrdGroup = "sriovfec.intel.com"
    sriovCrdVersion = "v2"
    sriovCrdNamespace = "vran-acceleration-operators"
    sriovCrdPlural = "sriovfecnodeconfigs"
    COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
    # Watch for events
    w = watch.Watch()
    for event in w.stream(COApi.list_namespaced_custom_object, sriovCrdGroup, sriovCrdVersion, sriovCrdNamespace, sriovCrdPlural):
        event_object = event['object']
        # In sriovfecnodeconfigs the CR name is same as the name of the node
        nodeName = event_object.get('metadata', {}).get('name', '')
        accelDevices = event_object.get('status', {}).get('inventory', {}).get('sriovAccelerators', [])
        accelConfigs = event_object.get('spec', {}).get('physicalFunctions', [])
        conditions = event_object.get('status', {}).get('conditions', {})
        mappedAccelDevices = []
        accelCrdStatus = COApi.get_namespaced_custom_object_status(accelCrdGroup, accelCrdVersion, accelCrdNamespace, accelCrdPlural, accelCrdName)
        accelCrdInventory = accelCrdStatus.get('hwAccelList', [])
        for accelDevice in accelDevices:
            specificConfig = {}
            # Find a config that was set for this accel
            for accelConfig in accelConfigs:
                if accelConfig.get('pciAddress', '') == accelDevice.get('pciAddress', ''):
                    specificConfig = accelConfig
            deviceID = accelDevice.get('deviceID', '')
            driver = accelDevice.get('driver', '')
            maxVirtualFunctions = accelDevice.get('maxVirtualFunctions', '')
            pciAddress = accelDevice.get('pciAddress', '')
            vendorID = accelDevice.get('vendorID', '')
            aalLpus = []
            for virtualFunction in accelDevice.get('virtualFunctions', []):
                lpuDeviceID = virtualFunction.get('deviceID', '')
                lpuDriver = virtualFunction.get('driver', '')
                lpuPciAddress = virtualFunction.get('pciAddress', '')
                # aalLpuId is created using nodeName and pciAddress, aalLpuHandle is pciAddress
                aalLpus.append({
                    "aalLpuId": nodeName + "-" + lpuPciAddress,
                    "aalLpuHandle": lpuPciAddress,
                    "imageLocation": lpuDriver,
                    "operationalState": "ENABLED"
                })
            # Since serial number is not available, it is created from nodeName and pciAddress
            # Some params are set by default: 
            # lpuType: Singe, all lpus are the same
            # operationalState: enabled, sriov-operator does not have a value like this
            mappedAccelDevices.append({
                "model": deviceID,
                "serialNum": nodeName + "-" + pciAddress,
                "imageLocation": driver,
                "vendorName": vendorID,
                "maxNumAalLpus": maxVirtualFunctions,
                "lpuType": "Single",
                "numAalLpusConfigured": specificConfig.get('vfAmount', None),
                "aalLpu": copy.deepcopy(aalLpus),
                "operationalConditions": conditions,
                "operationalState": "ENABLED",
                "extensions": [{
                    'bbDevConfig': copy.deepcopy(specificConfig.get('bbDevConfig', {})),
                    "node": nodeName,
                    "pciAddress": specificConfig.get('pciAddress', "")
                    }]
            })
        
        # Check if accelCrdInventory already has the accelDevice, 
        # Replace it if it is there, add it if it is not
        for mappedAccelDevice in mappedAccelDevices:
            found = False
            for accelDevice in accelCrdInventory:
                if accelDevice.get("serialNum", "") == mappedAccelDevice.get("serialNum", ""):
                    accelDevice.update(mappedAccelDevice)
                    found = True
            if not found:
                accelCrdInventory.append(mappedAccelDevice)
        
        body = [{"op": "add", "path": "/status", "value": {"hwAccelList": accelCrdInventory}}]
        COApi.patch_namespaced_custom_object_status(accelCrdGroup, accelCrdVersion, accelCrdNamespace, accelCrdPlural, accelCrdName, body)

