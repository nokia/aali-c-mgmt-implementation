#!/bin/bash

NODE_NAME=$(kubectl get nodes --no-headers | awk '{print $1}' | head -n 1)
CLUSTER_IP=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $3}')
SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers -n default | awk '{print $5}' | awk -F: '{print $1}')
SERVER_ADDRESS=${CLUSTER_IP}:${SERVER_PORT}
SCRIPT_DIR=$(dirname "$(realpath $0)")

filename="${SCRIPT_DIR}/../testconfig/setAalAccelConfig.json"

CONFIG_DATA=$(<"$filename")

# /setAalAccelIdentifier
curl --noproxy "*" -s -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num1234", "hw_accel_id": "test-id-1234"}' ${SERVER_ADDRESS}/setAalAccelIdentifier

curl --noproxy "*" -s -X POST -H "Content-Type: application/json" -d '{"vendor_name": "my-company", "model": "Model123", "serial_number": "Num5678", "hw_accel_id": "test-id-5678"}' ${SERVER_ADDRESS}/setAalAccelIdentifier

# /setAalAccelConfig
curl --noproxy "*" -s -X POST -H "Content-Type: application/json" -d "${CONFIG_DATA}" ${SERVER_ADDRESS}/setAalAccelConfig
