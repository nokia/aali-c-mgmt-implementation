import json, os
from kubernetes import client, config

def get_aal_fault_subscription(subscription_ids: list = None):
    config.load_incluster_config()
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    v1API = client.CoreV1Api()
    config_map_name = os.environ["FAULT_SUBSCRIPTION_NAME"]
    config_map = v1API.read_namespaced_config_map(name=config_map_name, namespace=namespace)

    all_fault_subscriptions = json.loads(config_map.data.get('subscriptions'))
    
    return_data = []
    for fault_subscription in all_fault_subscriptions:
        if fault_subscription.get('subscription_id', "") in subscription_ids or subscription_ids == None:
            return_data.append({"subscription_id": fault_subscription.get('subscription_id', ""), "filter_criteria": fault_subscription.get('filter_criteria', ""), "status_of_operation": "success"})
    
    return {
        "subscriptions": return_data
        }
