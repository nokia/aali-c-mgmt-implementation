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
SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers  -n default | awk '{print $5}' | awk -F: '{print $2}' | awk -F/ '{print $1}')
SERVER_ADDRESS=${NODE_URL}:${SERVER_PORT}


filename="testconfig/setAalAccelConfig.json"

CONFIG_DATA=$(<"$filename")

# /setAalAccelIdentifier
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num1234", "hw_accel_id": "test-id-1234"}' ${SERVER_ADDRESS}/setAalAccelIdentifier
check_response "response_body.json" "expected_responses/setAalAccelIdentifier.json" "setAalAccelIdentifier"

curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num5678", "hw_accel_id": "test-id-5678"}' ${SERVER_ADDRESS}/setAalAccelIdentifier
check_response "response_body.json" "expected_responses/setAalAccelIdentifier.json" "setAalAccelIdentifier"

# /getAalHwAccelStatus
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelStatus
check_response "response_body.json" "expected_responses/getAalHwAccelStatus.json" "getAalHwAccelStatus"

# /getAalLpuStatus
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"], "aal_lpu_handle": "lpu-handle-1234"}' ${SERVER_ADDRESS}/getAalLpuStatus
check_response "response_body.json" "expected_responses/getAalLpuStatus.json" "getAalLpuStatus"

# /getAalAccelInfo
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"]}' ${SERVER_ADDRESS}/getAalAccelInfo
check_response "response_body.json" "expected_responses/getAalAccelInfo.json" "getAalAccelInfo"

# /setAalAccelConfig
curl --noproxy "*" -s -o response_body.json -X POST -H "Content-Type: application/json" -d "${CONFIG_DATA}" ${SERVER_ADDRESS}/setAalAccelConfig
check_response "response_body.json" "expected_responses/setAalAccelConfig.json" "setAalAccelConfig"
