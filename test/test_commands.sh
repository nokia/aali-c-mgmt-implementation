#!/bin/bash

NODE_NAME=$(kubectl get nodes --no-headers | awk '{print $1}' | head -n 1)
CLUSTER_IP=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $3}')
SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $5}' | awk -F: '{print $1}')
SERVER_ADDRESS=${CLUSTER_IP}:${SERVER_PORT}

filename="test/testconfig/setAalAccelConfig.json"

CONFIG_DATA=$(<"$filename")

# /setAalAccelIdentifier
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num1234", "hw_accel_id": "test-id-1234"}' ${SERVER_ADDRESS}/setAalAccelIdentifier
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num5678", "hw_accel_id": "test-id-5678"}' ${SERVER_ADDRESS}/setAalAccelIdentifier

# /getAalHwAccelStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelStatus

# /setAalAccelConfig
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d "${CONFIG_DATA}" ${SERVER_ADDRESS}/setAalAccelConfig

# /getAalHwAccelStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelStatus

# /getAalAccelInfo
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"]}' ${SERVER_ADDRESS}/getAalAccelInfo

# /getAalLpuStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"], "aal_lpu_handle": "test-handle-5678"}' ${SERVER_ADDRESS}/getAalLpuStatus

# /getAalHwAccelFaults
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelFaults

# /getAalLpuFaults
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"], "aal_lpu_handle": "test-handle-5678"}' ${SERVER_ADDRESS}/getAalLpuFaults

# /createAalFaultSubscription
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"subscriptions":[{"subscription_id":"id1234", "filter_criteria": "[{\"faultId\": \"TemperatureFault\", \"resourceType\": \"HW-Accel\", \"resourceId\": \"test-id-1234\"}]"}]}' ${SERVER_ADDRESS}/createAalFaultSubscription

# /getAalFaultSubscription
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"subscription_id":["id1234"]}' ${SERVER_ADDRESS}/getAalFaultSubscription

# Create a HW-Accel fault
kubectl patch accelclusterconfigs.accel.example.com accelclusterconfig --subresource='status' --type='json' -p='[{"op": "add", "path": "/status/hwAccelList/0/faults", "value": [{"faultId": "TemperatureFault", "detectedTime": "123456789"}]}]' -n default

# Create a AAL-LPU fault
kubectl patch accelclusterconfigs.accel.example.com accelclusterconfig --subresource='status' --type='json' -p='[{"op": "add", "path": "/status/hwAccelList/0/aalLpu/0/faults", "value": [{"faultId": "MemoryExhausted", "detectedTime": "123456789"}]}]' -n default

# /deleteAalFaultSubscription
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"subscription_id":["id1234"]}' ${SERVER_ADDRESS}/deleteAalFaultSubscription

# /startAalLpu
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234", "aal_lpu_handle":"test-handle-5678"}' ${SERVER_ADDRESS}/startAalLpu

# /stopAalLpu
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234", "aal_lpu_handle":"test-handle-5678"}' ${SERVER_ADDRESS}/stopAalLpu
