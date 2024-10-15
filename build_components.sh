#!/bin/bash
CONTAINER_TOOL=${CONTAINER_TOOL:="podman"}

# Build images
sudo ${CONTAINER_TOOL} build . -t o-ran-interface:latest
sudo ${CONTAINER_TOOL} build test/ims_test/ -t o-ran-ims:latest
sudo ${CONTAINER_TOOL} build test/accel_controller_test/ -t accelclusterconfig-controller:latest
sudo ${CONTAINER_TOOL} build test/intel_test/ -t intel-accelclusterconfig-controller:latest
