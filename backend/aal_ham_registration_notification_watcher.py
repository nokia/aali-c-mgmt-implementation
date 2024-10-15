import requests, os
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from utils import accel_cr_mapping, get_accel_info, aal_inventory_notification, get_accel_cr_status
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    filename=os.environ["LOG_DIRECTORY"] + "/aalHamRegistrationNotificationWatcher.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def aal_ham_registration_notification_watcher():
    try:
        ham_crd_group = os.environ["HAMCRD_GROUP"]
        ham_crd_version = os.environ["HAMCRD_VERSION"]
        ham_crd_namespace = os.environ["HAMCRD_NAMESPACE"]
        ham_crd_plural = os.environ["HAMCRD_NAME_PLURAL"]
        ham_crd_name = os.environ["HAMCRD_NAME"]
        config.load_incluster_config()
        COApi = client.CustomObjectsApi()
        COApi.api_client.set_default_header('Content-Type', 'application/json-patch+json')
        old_ham_crd_spec = {}
        old_ham_operational_state = ""
        w = watch.Watch()
        for event in w.stream(COApi.list_namespaced_custom_object, ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural):
            detected_time = str(datetime.now().isoformat())
            event_object = event['object']
            ham_crd_spec = event_object.get("spec", {})
            ham_crd_status = event_object.get("status", {})
            ham_operational_state = ham_crd_status.get("aalHam", {}).get("operationalState", "")
            # Trigger new registration when registrationServiceEndpoint, localServiceEndpoint or HAM OperationalState changes
            if ham_crd_spec != old_ham_crd_spec or old_ham_operational_state != ham_operational_state:
                ims_endpoint_url = ham_crd_spec.get("aalHam", {}).get("registrationServiceEndpoint", "")
                o_ran_interface_service_endpoint = ham_crd_spec.get("aalHam", {}).get("localServiceEndpoint", "")
                try:
                    # Initally the status is empty, it needs to be populated
                    if ham_crd_status == {}:
                        body = [{"op": "replace", "path": "/status", "value": {}}]
                        COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                    if ham_crd_status.get("aalHam", {}) == {}:
                        body = [{"op": "replace", "path": "/status/aalHam", "value": {}}]
                        COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                    body = [{"op": "replace", "path": "/status/aalHam/imsRegistrationState", "value": "NOTREGISTERED"}]
                    COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                    data = {
                        'aalHam_ep': o_ran_interface_service_endpoint
                    }
                    # Only notify when HAM is ENABLED and both urls found
                    if ham_operational_state == "ENABLED" and ims_endpoint_url != "" and o_ran_interface_service_endpoint != "" :
                        try:
                            response = requests.post(ims_endpoint_url + "/aalHamRegistrationNotification", json=data)
                            if response.status_code == 200:
                                body = [{"op": "replace", "path": "/status/aalHam/imsRegistrationState", "value": "REGISTERED"}]
                                COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                                body = [{"op": "replace", "path": "/status/aalHam/registrationServiceEndpoint", "value": ims_endpoint_url}]
                                COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                                body = [{"op": "replace", "path": "/status/aalHam/localServiceEndpoint", "value": o_ran_interface_service_endpoint}]
                                COApi.patch_namespaced_custom_object_status(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                                logging.info(f"Successfully set interface endpoint to ims")

                                # Should send inventory notification when new connection between IMS and Interface
                                # All resources are then "ADDED"
                                accel_config_status = get_accel_cr_status.get_accel_cr_status()
                                accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)
                                mapped_accel_device_list = get_accel_info.get_accel_info(accel_devices).get("resources", [])
                                filtered_accel_device_list = filter_inventory(mapped_accel_device_list)
                                aal_inventory_notification.aal_inventory_notification({}, filtered_accel_device_list, detected_time, [])
                            else:
                                logging.error(f"Failed to send event: {response.status_code}, {response.text}")
                        except requests.exceptions.RequestException as e:
                            logging.error(f"Error sending event: {e}")
                        except Exception as e:
                            logging.error("Exception: %s\n" % e)
                    else:
                        logging.error("Ham not operational or urls not found")
                except ApiException as e:
                    logging.error("Some Kubernetes api issue: %s\n" % e)
                except Exception as e:
                    logging.error("Error: %s\n" % e)
            old_ham_crd_spec = ham_crd_spec
            old_ham_operational_state = ham_operational_state
    except Exception as e:
        logging.error("Exception: %s\n" % e)

# Filter out fields that do not trigger inventory notification and are not part of the resources
def filter_inventory(accel_device_list: list):
    for accel_device in accel_device_list:
        accel_device.pop("hw_accel_operational_state", None)
        accel_device.pop("hw_accel_operational_conditions", None)
        accel_device.pop("faults", None)
        for lpu in accel_device.get("aal_lpu_list", []):
            lpu.pop("aal_lpu_operational_state", None)
            lpu.pop("aal_lpu_operational_conditions", None)
            lpu.pop("faults", None)
    return accel_device_list

if __name__ == "__main__":
    aal_ham_registration_notification_watcher()
