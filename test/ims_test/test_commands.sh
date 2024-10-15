#!/bin/sh

NODE_URL=$(kubectl get nodes --no-headers | awk '{print $1}' | head -n 1)
IMS_SERVER_PORT=$(kubectl get svc o-ran-ims-svc --no-headers  | awk '{print $5}' | awk -F: '{print $2}' | awk -F/ '{print $1}')
IMS_SERVER_ADDRESS=${NODE_URL}:${IMS_SERVER_PORT}
HAM_ENDPOINT=${NODE_URL}:${INTERFACE_SERVER_PORT}

# /aalHamRegistrationNotification
curl -X POST -H "Content-Type: application/json" -d '{"aalHam_ep":${HAM_ENDPOINT}}' ${IMS_SERVER_ADDRESS}/aalHamRegistrationNotification

# /getHWAccels
curl ${SERVER_ADDRESS}/getHWAccels

# /getAalHwAccelStatus
curl -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":"bc00"}' ${IMS_SERVER_ADDRESS}/hamAPI/getAalHwAccelStatus

# /getAalAccelInfo
curl -X POST -H "Content-Type: application/json" -d '{"hw_accel_id":["bc00"]}' ${IMS_SERVER_ADDRESS}/hamAPI/getAalAccelInfo

# /setAalAccelIdentifier
curl -X POST -H "Content-Type: application/json" -d '{"vendor_name": "Vendor1", "model": "Model123", "serial_number": "Num1234", "hw_accel_id": "AccelID1234"}' ${IMS_SERVER_ADDRESS}/hamAPI/setAalAccelIdentifier

# /aalFaultNotification
curl -X POST -H "Content-Type: application/json" -d '{"subscription_id": "test1", "faults": [ {"hw_accel_id": "test", "aal_lpu_handle": "test", "detected_time": "test","event": "test","fault_id": "test"}]}' ${IMS_SERVER_ADDRESS}/aalFaultNotification