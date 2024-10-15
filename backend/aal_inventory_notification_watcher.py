import os
from kubernetes import client, config, watch
from utils import accel_cr_mapping, get_accel_info, aal_inventory_notification, get_accel_cr_status
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    filename=os.environ["LOG_DIRECTORY"] + "/aalInventoryNotificationWatcher.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def aal_inventory_notification_watcher():
    try:
        config.load_incluster_config()
        COApi = client.CustomObjectsApi()
        group = os.environ["ACCELCRD_GROUP"]
        version = os.environ["ACCELCRD_VERSION"]
        namespace = os.environ["ACCELCRD_NAMESPACE"]
        plural = os.environ["ACCELCRD_NAME_PLURAL"]

        accel_config_status = get_accel_cr_status.get_accel_cr_status()
        accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)
        mapped_accel_device_list = get_accel_info.get_accel_info(accel_devices).get("resources", [])
        old_filtered_accel_device_list = filter_inventory(mapped_accel_device_list)

        resource_list = []
        # Watch for events
        w = watch.Watch()
        for event in w.stream(COApi.list_namespaced_custom_object, group, version, namespace, plural):
            detected_time = str(datetime.now().isoformat())
            event_object = event['object']
            accel_devices = accel_cr_mapping.get_hw_accel_list(event_object.get('status', {}))
            mapped_accel_device_list = get_accel_info.get_accel_info(accel_devices).get("resources", [])
            new_filtered_accel_device_list = filter_inventory(mapped_accel_device_list)

            # Inventory notification is only triggered for certain changes
            if old_filtered_accel_device_list != new_filtered_accel_device_list:
                aal_inventory_notification.aal_inventory_notification(old_filtered_accel_device_list, new_filtered_accel_device_list, detected_time, resource_list)
            old_filtered_accel_device_list = new_filtered_accel_device_list
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
    aal_inventory_notification_watcher()
