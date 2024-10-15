VERSION ?= latest
REGISTRY ?= localhost
DOCKERFILE ?= Dockerfile
BASE_IMAGE_REPO ?= docker.io/library/
CONTAINER_TOOL ?= podman
NAMESPACE ?= default
SRIOV_NAMESPACE ?= vran-acceleration-operators

.PHONY: build-interface
build-interface:
	@echo "Building image..."
	sudo ${CONTAINER_TOOL} build . -t ${REGISTRY}/o-ran-interface:${VERSION}

.PHONY: build-test-ims
build-test-ims:
	@echo "Building image..."
	sudo ${CONTAINER_TOOL} build test/ims_test/ -t ${REGISTRY}/o-ran-ims:${VERSION}

.PHONY: build-test-crd-controller
build-test-crd-controller:
	@echo "Building image..."
	sudo ${CONTAINER_TOOL} build test/accel_controller_test/ -t ${REGISTRY}/accelclusterconfig-controller:${VERSION}

.PHONY: build-all
build-all:
	@echo "Building images..."
	sudo ${CONTAINER_TOOL} build . -t ${REGISTRY}/o-ran-interface:${VERSION}
	sudo ${CONTAINER_TOOL} build test/ims_test/ -t ${REGISTRY}/o-ran-ims:${VERSION}
	sudo ${CONTAINER_TOOL} build test/accel_controller_test/ -t ${REGISTRY}/accelclusterconfig-controller:${VERSION}

.PHONY: helm-install-interface
helm-install-interface:
	@echo "Uninstalling old installations..."
	helm uninstall o-ran-interface --ignore-not-found -n ${NAMESPACE}

	@echo "Installing AALI-C-Mgmt interface (o-ran-interface)..."
	helm install o-ran-interface helm/ --set ims.endpoint=${IMS_SERVER_ADDRESS} --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

.PHONY: helm-install-all-test
helm-install-all-test:
	@echo "Installing IMS (o-ran-ims)..."
	helm install o-ran-ims test/ims_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

	@echo "Getting IMS server address and installing AALI-C-Mgmt interface (o-ran-interface)..."
	@IMS_SERVER_URL=$$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $$3}'); \
	IMS_SERVER_PORT=$$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $$5}' | awk -F: '{print $$1}'); \
	helm install o-ran-interface helm/ \
		--set ims.endpoint=http://$${IMS_SERVER_URL}:$${IMS_SERVER_PORT} \
		--set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

	@echo "Installing CR Controller (accelclusterconfig-controller)..."
	helm install accelclusterconfig-controller test/accel_controller_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

.PHONY: helm-uninstall-all-test
helm-uninstall-all-test:
	@echo "Uninstalling old installations..."
	helm uninstall o-ran-ims --ignore-not-found -n ${NAMESPACE}
	helm uninstall o-ran-interface --ignore-not-found -n ${NAMESPACE}
	helm uninstall accelclusterconfig-controller --ignore-not-found -n ${NAMESPACE}

	@echo "Deleting old custom resources and custom resource definitions..."
	kubectl delete crd hamconfigs.accel.example.com --ignore-not-found=true
	kubectl delete crd accelclusterconfigs.accel.example.com --ignore-not-found=true

.PHONY: helm-install-intel-test
helm-install-intel-test:
	@echo "Installing IMS (o-ran-ims)..."
	helm install o-ran-ims test/ims_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

	@echo "Getting IMS server address and installing AALI-C-Mgmt interface (o-ran-interface)..."
	@IMS_SERVER_URL=$$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $$3}'); \
	IMS_SERVER_PORT=$$(kubectl get svc o-ran-ims-svc --no-headers -n ${NAMESPACE} | awk '{print $$5}' | awk -F: '{print $$1}'); \
	helm install o-ran-interface helm/ \
		--set ims.endpoint=http://$${IMS_SERVER_URL}:$${IMS_SERVER_PORT} \
		--set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${NAMESPACE}

	@echo "Installing Intel CR Controller (intel-accelclusterconfig-controller)..."
	helm install intel-accelclusterconfig-controller test/intel_test/helm --set image.repository=${REGISTRY} --set image.tag=${VERSION} -n ${SRIOV_NAMESPACE}

.PHONY: helm-uninstall-intel-test
helm-uninstall-intel-test:
	@echo "Uninstalling old installations..."
	helm uninstall o-ran-ims --ignore-not-found -n ${NAMESPACE}
	helm uninstall o-ran-interface --ignore-not-found -n ${NAMESPACE}
	helm uninstall intel-accelclusterconfig-controller --ignore-not-found -n ${SRIOV_NAMESPACE}

	@echo "Deleting old custom resources and custom resource definitions..."
	kubectl delete crd hamconfigs.accel.example.com --ignore-not-found=true
	kubectl delete crd accelclusterconfigs.accel.example.com --ignore-not-found=true