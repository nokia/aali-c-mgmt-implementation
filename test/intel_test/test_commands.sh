#!/bin/bash

NODE_NAME=$(kubectl get nodes --no-headers | awk '{print $1}' | head -n 1)
CLUSTER_IP=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $3}')
SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $5}' | awk -F: '{print $1}')
SERVER_ADDRESS=${CLUSTER_IP}:${SERVER_PORT}

filename="sample_config/setAalAccelConfig_Intel.json"

CONFIG_DATA=$(<"$filename")

# /setAalAccelIdentifier
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"vendor_name": "8086", "model": "57c0", "serial_number": "'"${NODE_NAME}"'-0000:f7:00.0", "hw_accel_id": "test-id-1234"}' ${SERVER_ADDRESS}/setAalAccelIdentifier

# /getAalHwAccelStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelStatus

# /setAalAccelConfig
curl --noproxy "*"  -X POST -H "Content-Type: application/json" -d "${CONFIG_DATA}" ${SERVER_ADDRESS}/setAalAccelConfig

# /getAalHwAccelStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"test-id-1234"}' ${SERVER_ADDRESS}/getAalHwAccelStatus

# /getAalAccelInfo
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"]}' ${SERVER_ADDRESS}/getAalAccelInfo

# /getAalLpuStatus
curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["test-id-1234"], "aal_lpu_handle": "test-handle-5678"}' ${SERVER_ADDRESS}/getAalLpuStatus