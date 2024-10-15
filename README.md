# aali-c-mgmt-implementation

This repository contains an implementation for the AALI-C-Mgmt specification, according to O-RAN.WG6.AAL Common API-R003-v07.00. The specification can be found at the [O-RAN Alliance web page](https://specifications.o-ran.org/specifications). The implementation is a FastAPI server in a Kubernetes environment.

## Architecture

The aali-c-mgmt-implementation communicates to a backend via the accelclusterconfig custom resource. The Interface expects that a accelerator/vendor specific controller monitors the accelclusterconfig and does operations according to parameters set. An example of how the controller could work is shown in [accel_controller_test](test/accel_controller_test/).

## Installing
Requires enviroment with Kubernetes and Helm.

1. Build the container image 
    * `make CONTAINER_TOOL=podman REGISTRY=localhost VERSION=latest build-interface`
2. Deploy with helm
    * `make IMS_SERVER_ADDRESS="" REGISTRY=localhost VERSION=latest NAMESPACE=default helm-install-interface`
3. Get `clusterIP` of the interface
    * `kubectl get svc o-ran-interface-svc --no-headers -n default  | awk '{print $3}'`
4. Access `o-ran-interface` operations at `<clusterIP>:5000/<operation>`

## Status of implemented operations

The operations below are defined in the O-RAN Acceleration Abstraction Layer Common API documentation. Operations which are not fully defined by O-RAN yet (as of O-RAN.WG6.AAL Common API-R003-v07.00) are not included. 

| Operation                         | Status        | Additional info   |
| --------------------------------- | ------------- | ----------------- |
| getAalHwAccelStatus               | Implemented   |                   |
| getAalLpuStatus                   | Implemented   |                   |
| getAalAccelInfo                   | Implemented   |                   |
| setAalAccelConfig                 | Implemented   |                   |
| setAalAccelIdentifier             | Implemented   |                   |
| aalInventoryNotification          | Implemented   |                   |
| getAalHwAccelFaults               | Implemented   |                   |
| getAalLpuFaults                   | Implemented   |                   |
| createAalFaultSubscription        | Implemented   |                   |
| deleteAalFaultSubscription        | Implemented   |                   |
| getAalFaultSubscription           | Implemented   |                   |
| aalFaultNotification              | Implemented   |                   |
| startAalLpu                       | Implemented   |                   |
| stopAalLpu                        | Implemented   |                   |
| aalHamRegistrationNotification    | Implemented   |                   |


For example, using `/getAalHwAccelStatus`

```sh
curl -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"id-1234"}' localhost:5000/getAalHwAccelStatus
```

```json
{"hw_accel_operational_conditions":"","hw_accel_operational_state":"Available","status_of_operation":""}
```


## Operations that set new parameters

The operations below set new parameters:

| Operation                     | 
| ----------------------------- | 
| setAalAccelConfig             | 
| setAalAccelIdentifier         | 
| startAalLpu                   | 
| stopAalLpu                    | 

These operations work by replacing a part of the `AccelClusterConfig` custom resource with a kubectl patch request on the `spec` field of the custom resource. The HAM then detectes the changes in the custom resource and does operations based on the changes. When the operations are complete, the HAM updates the `status` field of the custom resource.

## Data validation

For data validation the fastapi server uses Pydantic Basemodel library for requests and responses.

## Testing

The /test directory provides tests for the O-RAN-Interface. Two components are provided for functional testing, a dummy IMS and accelclusterconfig controller. One component is provided for real world testing, a accelclusterconfig controller for the Intel SRIOV-FEC Operator. The dummy IMS is used to test the `aal_fault_notification`, `aal_ham_registration_notification` and `aal_inventory_notification` commands. The accelclusterconfig controller is used for testing all commands that query or set information to the underlying hardware. It provides a deploys the accelclusterconfig custom resource and a controller for it. The `make helm-install-all-test` command installs the O-RAN-Interface, dummy IMS and accelclusterconfig controller. To install the Intel specific component, the components should be installed individually.

### accel_controller_test

The accel_controller_test folder has a controller for the accelclusterconfig. This controller monitors the spec of the accelclusterconfig and updates the status accordingly. It does not do any actual operations.

### ims_test

The ims_test folder has a IMS implementation. The IMS is a Flask server, which is used to test the commands from the O-RAN-Interface that need the IMS.

### intel_test

The intel_test folder has a controller for the accelclusterconfig. This controller monitors the spec of the accelclusterconfig and does operations on the Intel SRIOV-FEC Operator. Only a couple operations are currently supported. Check [README](test/intel_test/helm/README.md) for more information.

### Workflows

The workflows folder has two different functional tests for the interface, HW_Accelerator_installation_test and fault_notification_test. They both use the accel_controller_test components. They require the interface and accel_controller_test components to be running, by for example using `make helm-install-all-test`. Then the tests can be run with their `execute_test.sh` scripts.

### test_commands.sh

The test_commands.sh file has examples of commands that can be run when the components have been installed with `make helm-install-all-test`.


## Fault notifications

The interface uses the ConfigMap `fault-subscriptions` to store information about fault subscriptions. When the interface component is first launched, an empty `fault-subscriptions` ConfigMap is created. When using the `createAalFaultSubscription` operation, the data section of the ConfigMap is populated with the new fault subscription. 

| Operation                     | 
| -----------                   | 
| createAalFaultSubscription    |
| deleteAalFaultSubscription    |
| getAalFaultSubscription       |
| aalFaultNotification          |

The `filter_criteria` differs from the example in the AAL Common API specification documentation. However, the specification states that the exact implementation is protocol specific. For this implementation the fault subscription needs to be in the style below:
```json
    "filter_criterias" = [{
        "faultId": "",
        "resourceType": "",
        "resourceId": ""
    }]
```
Where `faultId` is any `faultId` a resource can get, for example `TemperatureFault` or `MemoryExhausted`, `resourceType` is either `HW-Accel` or `AAL-LPU` and `resourceId` is either `hwAccelId` or `aalLpuHandle` depending on which `resourceType` was selected. The wildcard `*` can be used on any of the criterions to select them all.

Example:

```json
    "filter_criterias" = [{
        "faultId": "TemperatureFault",
        "resourceType": "HW-Accel",
        "resourceId": "id-12345"
    },
    {
        "faultId": "MemoryExhausted",
        "resourceType": "AAL-LPU",
        "resourceId": "4"
    }
    ]
```

Note: when creating fault subscription the `filter_criteria` -field is a string
`createAalFaultSubscription`, thus quotes need to be escaped:

```sh
curl -X POST -H "Content-Type: application/json" -d '{"subscriptions":[{"subscription_id":"id1234", "filter_criteria": "[{\"faultId\": \"TemperatureFault\", \"resourceType\": \"HW-Accel\", \"resourceId\": \"id-12345\"}]"}]}' ${SERVER_ADDRESS}/createAalFaultSubscription
```


