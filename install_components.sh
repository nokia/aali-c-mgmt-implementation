#!/bin/bash

NAMESPACE=default
VERSION=latest
REGISTRY=localhost

# Delete old installations 

helm uninstall o-ran-ims --ignore-not-found -n ${NAMESPACE}
helm uninstall o-ran-interface --ignore-not-found -n ${NAMESPACE}
helm uninstall accelclusterconfig-controller --ignore-not-found -n ${NAMESPACE}

# Install IMS (o-ran-ims)
helm install o-ran-ims test/ims_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

# Get IMS server address
SERVICE_URL=$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $3}' )

# IMS port should be 5000 always
IMS_SERVER_PORT=$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $5}' | awk -F: '{print $1}')
IMS_SERVER_ADDRESS=http://${SERVICE_URL}:${IMS_SERVER_PORT}

# Install CRD Controller (accelclusterconfig-controller)
helm install accelclusterconfig-controller test/accel_controller_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

# Install AALI-C-Mgmt interface (o-ran-interface)
helm install o-ran-interface helm/ --set ims.endpoint=$IMS_SERVER_ADDRESS --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

# Get interface server address
export NODE_URL=$(kubectl get nodes --no-headers -n ${NAMESPACE} | awk '{print $1}' | head -n 1)
export INTERFACE_SERVER_PORT=$(kubectl get svc o-ran-interface-svc --no-headers -n ${NAMESPACE} | awk '{print $5}' | awk -F: '{print $2}' | awk -F/ '{print $1}')
export INTERFACE_SERVER_ADDRESS=${NODE_URL}:${SERVER_PORT}