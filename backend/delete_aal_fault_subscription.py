import json, os
from kubernetes import client, config

def delete_aal_fault_subscription(subscriptions: list):
    config.load_incluster_config()
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    v1API = client.CoreV1Api()
    config_map_name = os.environ["FAULT_SUBSCRIPTION_NAME"]
    config_map = v1API.read_namespaced_config_map(name=config_map_name, namespace=namespace)

    all_fault_subscriptions = json.loads(config_map.data.get('subscriptions'))
    
    new_all_fault_subscriptions = [fault_subscription for fault_subscription in all_fault_subscriptions if fault_subscription["subscription_id"] not in subscriptions]

    config_map.data['subscriptions'] = json.dumps(new_all_fault_subscriptions)
    v1API.replace_namespaced_config_map(name=config_map_name, namespace=namespace, body=config_map)
    
    deleted_subscriptions = []
    for fault_subscription in all_fault_subscriptions:
        if fault_subscription not in new_all_fault_subscriptions:
            fault_subscription["status_of_operation"] = "success"
            deleted_subscriptions.append(fault_subscription)

    return {
        "subscriptions": deleted_subscriptions
        }
