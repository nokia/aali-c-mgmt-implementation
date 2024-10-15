import requests, os
from kubernetes import client, config
import logging

def aal_inventory_notification(old_filtered_accel_device_list: list, new_filtered_accel_device_list: list, detected_time: str, resource_list: list):
    config.load_incluster_config()
    COApi = client.CustomObjectsApi()
    ham_crd_group = os.environ["HAMCRD_GROUP"]
    ham_crd_version = os.environ["HAMCRD_VERSION"]
    ham_crd_namespace = os.environ["HAMCRD_NAMESPACE"]
    ham_crd_plural = os.environ["HAMCRD_NAME_PLURAL"]
    ham_crd_name = os.environ["HAMCRD_NAME"]
    ham_crd_status = COApi.get_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name).get("status", {})
    ims_endpoint_url = ham_crd_status.get("aalHam", {}).get("registrationServiceEndpoint", "")
    ims_registration_state = ham_crd_status.get("aalHam", {}).get("imsRegistrationState", "")
    resource_list = check_changes(old_filtered_accel_device_list, new_filtered_accel_device_list, detected_time, resource_list)
    data = {
        'resources': resource_list
    }
    if ims_endpoint_url != "" and ims_registration_state == "REGISTERED":
        try:
            response = requests.post(ims_endpoint_url + "/aalInventoryNotification", json=data)
            if response.status_code == 200:
                logging.info(f"Successfully sent aalInventoryNotification")
            else:
                logging.error(f"Failed to send aalInventoryNotification: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending aalInventoryNotification: {e}")
    else:
        logging.error("No IMS endpoint configured")

# Check where the changes are and their event type
def check_changes(old_filtered_accel_device_list: list, new_filtered_accel_device_list: list, detected_time: str, resource_list: list):
    new_resource_list = []
    for accel_index in range(len(new_filtered_accel_device_list)):
        old_index = get_index_in_other_device_list(new_filtered_accel_device_list[accel_index], old_filtered_accel_device_list)
        if old_index >= 0:
            # Modified
            if old_filtered_accel_device_list[old_index] != new_filtered_accel_device_list[accel_index]:
                new_resource_list.append({"resource": new_filtered_accel_device_list[accel_index] ,"detected_time": detected_time, "event": "Modify"})
            # No change, use old event
            else:
                # Check if accel can be found in old resource_list, if not then add it
                # Accel should always be found in old resource_list, only on first run it is not found
                if get_accel_index_in_resource_list(new_filtered_accel_device_list[accel_index], resource_list) >= 0:
                    new_resource_list.append(resource_list[get_accel_index_in_resource_list(new_filtered_accel_device_list[accel_index], resource_list)])
                
                else:
                    new_resource_list.append({"resource": new_filtered_accel_device_list[accel_index] ,"detected_time": detected_time, "event": "Add"})
        # Accel added 
        else:
            new_resource_list.append({"resource": new_filtered_accel_device_list[accel_index] ,"detected_time": detected_time, "event": "Add"})

    for i in range(len(old_filtered_accel_device_list)):
        index = get_index_in_other_device_list(old_filtered_accel_device_list[i], new_filtered_accel_device_list)
        # Accel device not found in new list = accel removed
        if index < 0:
            new_resource_list.append({"resource": old_filtered_accel_device_list[i] ,"detected_time": detected_time, "event": "Remove"})

    return new_resource_list

def get_accel_index_in_resource_list(accel_device: dict, resource_list: list):
    index = -1
    for i in range(len(resource_list)):
        if resource_list[i].get("resource", {}).get('serial_number', "") == accel_device.get("serial_number", "") and resource_list[i].get("resource", {}).get('vendor_name', "") == accel_device.get("vendor_name", "") and resource_list[i].get("resource", {}).get('model', "") == accel_device.get("model", ""):
            index = i
    return index

def get_index_in_other_device_list(accel_device: dict, accel_device_list: list):
    index = -1
    for i in range(len(accel_device_list)):
        if accel_device_list[i].get('serial_number', "") == accel_device.get("serial_number", "") and accel_device_list[i].get('vendor_name', "") == accel_device.get("vendor_name", "") and accel_device_list[i].get('model', "") == accel_device.get("model", ""):
            index = i
    return index

if __name__ == "__main__":
    aal_inventory_notification()
