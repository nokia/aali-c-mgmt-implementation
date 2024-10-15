#!/bin/bash

check_response() {
    response_body=$(<$1) 
    expected_string=$(<$2)
    operation=$3
    if diff <(jq --sort-keys . "$1") <(jq --sort-keys . "$2") > /dev/null; then
        echo "Response body is as expected in $operation"
    else
        echo "Unexpected response body in $operation"
        echo "Response recieved: $response_body"
        echo "Expected response: $expected_string"
        exit 1
    fi
}

NODE_URL=$(kubectl get nodes --no-headers | awk '{print $1}' | head -n 1)
SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $5}' | awk -F: '{print $2}' | awk -F/ '{print $1}')
SERVER_ADDRESS=${NODE_URL}:${SERVER_PORT}

../set_mock_config.sh

# /createAalFaultSubscription
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"subscriptions":[{"subscription_id":"id1234", "filter_criteria": "[{\"faultId\": \"TemperatureFault\", \"resourceType\": \"HW-Accel\", \"resourceId\": \"test-id-1234\"}]"}]}' ${SERVER_ADDRESS}/createAalFaultSubscription
check_response response_body.json expected_responses/createAalFaultSubscription.json "createAalFaultSubscription"

# /getAalFaultSubscription
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"subscription_id":["id1234"]}' ${SERVER_ADDRESS}/getAalFaultSubscription
check_response response_body.json expected_responses/getAalFaultSubscription.json "getAalFaultSubscription"

# Create a HW-Accel fault (CRD Specific)
kubectl patch accelclusterconfigs.accel.example.com accelclusterconfig --subresource='status' --type='json' -p='[{"op": "add", "path": "/status/hwAccelList/0/faults", "value": [{"faultId": "TemperatureFault", "detectedTime": "123456789"}]}]' -n default

# Create a AAL-LPU fault (CRD Specific)
kubectl patch accelclusterconfigs.accel.example.com accelclusterconfig --subresource='status' --type='json' -p='[{"op": "add", "path": "/status/hwAccelList/0/aalLpu/0/faults", "value": [{"faultId": "MemoryExhausted", "detectedTime": "123456789"}]}]' -n default

# /deleteAalFaultSubscription
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"subscription_id":["id1234"]}' ${SERVER_ADDRESS}/deleteAalFaultSubscription
check_response response_body.json expected_responses/deleteAalFaultSubscription.json "deleteAalFaultSubscription"
