import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

logging.basicConfig(
    level=logging.INFO,
    filename=os.environ["LOG_DIRECTORY"] + "/setUrlEndpoints.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def set_url_endpoints():
    config.load_incluster_config()
    v1API = client.CoreV1Api()
    COApi = client.CustomObjectsApi()
    ham_crd_group = os.environ["HAMCRD_GROUP"]
    ham_crd_version = os.environ["HAMCRD_VERSION"]
    ham_crd_namespace = os.environ["HAMCRD_NAMESPACE"]
    ham_crd_plural = os.environ["HAMCRD_NAME_PLURAL"]
    ham_crd_name = os.environ["HAMCRD_NAME"]
    interface_service_name = os.environ["INTERFACE_SVC_NAME"]
    interface_namespace = os.environ["MY_POD_NAMESPACE"]
    ims_endpoint_url = os.environ["IMS_ENDPOINT"]
    if os.environ["IMS_ENDPOINT"] != "":
        try:
            interface_service = v1API.read_namespaced_service(name=interface_service_name, namespace=interface_namespace)
            o_ran_interface_service_endpoint = "http://" + str(interface_service.spec.cluster_ip) + ":" + str(interface_service.spec.ports[0].port)
            body = {
                "spec": {
                    "aalHam": {
                        "registrationServiceEndpoint": ims_endpoint_url,
                        "localServiceEndpoint": o_ran_interface_service_endpoint
                    }
                }
            }
            try:
                COApi.patch_namespaced_custom_object(ham_crd_group, ham_crd_version, ham_crd_namespace, ham_crd_plural, ham_crd_name, body)
                logging.info("registrationServiceEndpoint and localServiceEndpoint set to HAM custom resource")
            except ApiException as e:
                logging.error("Exception when trying to patch ham crd: %s\n" % e)
        except ApiException as e:
            logging.error("Exception when trying to get interface service: %s\n" % e)
    else:
        logging.info("No registrationServiceEndpoint set")

if __name__ == "__main__":
    set_url_endpoints()