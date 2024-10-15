# o-ran-ims

This directory is for deploying an O-RAN IMS server to test the o-ran-interface. The is implemented with the Flask framework.

The server implements the following functions as defined by the O-RAN AALI-C-Mgmt specification:

| Operation      | Status | Additional info|
| ----------- | ----------- | ----------- |
| aalHamRegistrationNotification           | Implemented |  |
| aalFaultNotification               | Implemented |  |

Additionally one can use the server to access all of the functions provided by the interface by using the endpoint api:


```sh
curl localhost:5000/hamAPI/<operation>
```
eg.
```sh
curl localhost:5000/hamAPI/getHWAccels
```
## Deploy o-ran-ims
To use this test IMS follow these steps:

1. Build the container image with the `Dockerfile`
    * eg. `docker build . -t o-ran-ims:latest`
2. Deploy with helm
    * `cd helm`
    * Check that values in `values.yaml` are correct
    * `helm install o-ran-ims .`
3. Get `clusterIP`
    * `kubectl get svc o-ran-ims-svc --no-headers -n default  | awk '{print $3}'`
4. Deploy `o-ran-interface` 