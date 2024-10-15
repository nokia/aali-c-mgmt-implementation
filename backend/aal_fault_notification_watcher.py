import json, requests, os
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from utils import accel_cr_mapping
import logging

logging.basicConfig(
    level=logging.INFO,
    filename=os.environ["LOG_DIRECTORY"] + "/aalFaultNotificationWatcher.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def aal_fault_notification_watcher():
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    group = os.environ["ACCELCRD_GROUP"]
    version = os.environ["ACCELCRD_VERSION"]
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    plural = os.environ["ACCELCRD_NAME_PLURAL"]
    name = os.environ["ACCELCRD_NAME"]
    ham_crd_group = os.environ["HAMCRD_GROUP"]
    ham_crd_version = os.environ["HAMCRD_VERSION"]
    ham_crd_namespace = os.environ["HAMCRD_NAMESPACE"]
    ham_crd_plural = os.environ["HAMCRD_NAME_PLURAL"]
    ham_crd_name = os.environ["HAMCRD_NAME"]
    v1API = client.CoreV1Api()
    config_map_name = os.environ["FAULT_SUBSCRIPTION_NAME"]
    fault_array = []
    # Watch for changes in status
    w = watch.Watch()
    for event in w.stream(COApi.list_namespaced_custom_object, group, version, namespace, plural):
        event_object = event['object']
        new_status = event_object.get('status', {})
        try:
            config_map = v1API.read_namespaced_config_map(name=config_map_name, namespace=namespace)
            all_fault_subscriptions = json.loads(config_map.data.get('subscriptions', []))
            fault_array = find_faults(fault_array, new_status, all_fault_subscriptions)
            for fault_subscription in fault_array:
                if fault_array != []:
                    data = {
                        'subscription_id': fault_subscription.get("subscription_id", ""),
                        'faults': fault_subscription.get("faults", {})
                    }
                    try:
                        ham_crd_status = COApi.get_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name).get("status", {})
                        ims_endpoint_url = ham_crd_status.get("aalHam", {}).get("registrationServiceEndpoint", "")
                        ims_registration_state = ham_crd_status.get("aalHam", {}).get("imsRegistrationState", "")
                        if ims_endpoint_url != "" and ims_registration_state == "REGISTERED":
                            try:
                                response = requests.post(ims_endpoint_url + "/aalFaultNotification", json=data)
                                if response.status_code == 200:
                                    logging.info(f"Successfully sen fault notification to ims")
                                else:
                                    logging.error(f"Failed to send aalFaultNotification: {response.status_code}, {response.text}")
                            except requests.exceptions.RequestException as e:
                                logging.error(f"Error sending aalFaultNotification: {e}")
                        else:
                            logging.error("No IMS endpoint configured")
                    except ApiException as e:
                        logging.error("Exception when trying to get ham crd: %s\n" % e)
        except ApiException as e:
            logging.error("Exception when trying to read fault subscriptions ConfigMap: %s\n" % e)
        except Exception as e:
            logging.error("Exception: %s\n" % e)

# Find faults that are new or cleared
def find_faults(old_faults_array: list, new_status: dict, all_fault_subscriptions: list):
    new_faults_array = []
    current_faults_array = []
    new_accel_devices = accel_cr_mapping.get_hw_accel_list(new_status)
    fault_dict = {}
    for accel_device in new_accel_devices:
        for fault in accel_device.get("faults", []):
            fault_dict['fault_id'] = fault.get('faultId', None)
            fault_dict['detected_time'] = fault.get('detectedTime', None)
            fault_dict['hw_accel_id'] = accel_cr_mapping.get_hw_accel_id(accel_device)
            fault_dict['resourceType'] = 'HW-Accel'
            current_faults_array.append(fault_dict)
        for lpu in accel_device.get("aal_lpu_list", []):
            for fault in lpu.get("faults", []):
                fault_dict['fault_id'] = fault.get('faultId', None)
                fault_dict['detected_time'] = fault.get('detectedTime', None)
                fault_dict['aal_lpu_handle'] = accel_cr_mapping.get_lpu_handle(lpu)
                fault_dict['hw_accel_id'] = accel_cr_mapping.get_hw_accel_id(accel_device)
                fault_dict['resourceType'] = 'AAL-LPU'
                current_faults_array.append(fault_dict)
    
    # Remove event so fault dicts can be compared
    for fault in old_faults_array:
        fault.pop('event', None)
    
    # If the fault is not in the old_faults_array, a new fault is detected
    # Temporarely remove resourceType
    for fault in current_faults_array:
        resource_type = fault.pop('resourceType', None)
        if fault not in old_faults_array:
            fault['resourceType'] = resource_type
            fault['event'] = 'raise'
            new_faults_array.append(fault)

    
    # If an old fault is not in the new_faults_array, a fault is cleared
    # Temporarely remove resourceType
    for fault in old_faults_array:
        resource_type = fault.pop('resourceType', None)
        if fault not in new_faults_array:
            fault['resourceType'] = resource_type
            fault['event'] = 'clear'
            new_faults_array.append(fault)

    
    return_faults = []
    for fault_subscription in all_fault_subscriptions:
        subscription_faults = []
        for new_fault in new_faults_array:
            for criteria in json.loads(fault_subscription.get("filter_criteria", [])):
                if new_fault.get('fault_id', "") == criteria.get('faultId', "") or criteria.get('faultId', "") == "*":
                    if (criteria.get('resourceType', "") == "AAL-LPU" or criteria.get('resourceType', "") == "*") and (criteria.get('resourceId', "") == new_fault.get('aal_lpu_handle', "") or criteria.get('resourceId', "") == "*"):
                        new_fault.pop('resourceType', None)
                        subscription_faults.append(new_fault)
                    elif (criteria.get('resourceType', "") == "HW-Accel" or criteria.get('resourceType', "") == "*") and (criteria.get('resourceId', "") == new_fault.get('hw_accel_id', "") or criteria.get('resourceId', "") == "*"):
                        new_fault.pop('resourceType', None)
                        subscription_faults.append(new_fault)
        if subscription_faults != []:
            return_faults.append({"subscription_id": fault_subscription.get("subscription_id", ""), "faults": subscription_faults})
    
    return return_faults

if __name__ == "__main__":
    aal_fault_notification_watcher()
