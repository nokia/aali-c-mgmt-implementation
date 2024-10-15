import json, os
from kubernetes import client, config
import copy

def create_aal_fault_subscription(subscriptions: list):
    config.load_incluster_config()
    namespace = os.environ["ACCELCRD_NAMESPACE"]
    v1API = client.CoreV1Api()
    config_map_name = os.environ["FAULT_SUBSCRIPTION_NAME"]
    config_map = v1API.read_namespaced_config_map(name=config_map_name, namespace=namespace)

    all_fault_subscriptions = json.loads(config_map.data.get('subscriptions'))
    
    for subscription in subscriptions:
        all_fault_subscriptions.append(copy.deepcopy(subscription))
        subscription.pop("filter_criteria", None)
        subscription["status_of_operation"] = "success"

    config_map.data['subscriptions'] = json.dumps(all_fault_subscriptions)
    v1API.replace_namespaced_config_map(name=config_map_name, namespace=namespace, body=config_map)

    return {
        "subscriptions": subscriptions
        }
