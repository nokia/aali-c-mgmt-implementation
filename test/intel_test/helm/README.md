This chart deploys an intermidiate controller component so the AALI-C-Mgmt interface can work with the Intel SRIOV-FEC Operator. The controller reads values from the accelclusterconfig custom resource and sets them to the Intel SRIOV-FEC Operator specific custom resources.

Two controllers/watchers are started when the application is deployed. Controller.py creates the accelclusterconfig custom resource and starts watching it. It then triggers operations based on the changes in the spec. Controller.py also triggers the sriovfecnodeconfigs_watcher, which watches the sriocfecnodeconfigs and updates the accelclusterconfig when it notices changes.

Due to limitations in the Intel SRIOV-FEC Operator, only a handful of operations are currently supported with caveats. Other operations either give an error, do not give any info or do nothing. The operations that work somewhat are: 

| Operation       | Additional info|
| ----------- | ----------- |
| getAalHwAccelStatus                | No HWAccel status provided by Intel SRIOV-FEC Operator |
| getAalAccelInfo                    | Lots of info missing |
| setAalAccelConfig                  | Requires specific format, check [setAalAccelConfig](#setAalAccelConfig) |
| setAalAccelIdentifier              |  |
| aalInventoryNotification           |  |
| aalHamRegistrationNotification     |  |

# setAalAccelConfig
The JSON post to /setAalAccelConfig needs to be in the format below:

```json
{
  "hw_accel_list": [
      {
          "hw_accel_id": "test-id-1234",
          "hw_accel_image_version": "",
          "hw_accel_image_location": "vfio-pci",
          "hw_accel_vendor_specific": [
            {
              "bbDevConfig": {
                "acc200": {
                  "downlink4G": {
                    "aqDepthLog2": 4,
                    "numAqsPerGroups": 16,
                    "numQueueGroups": 4
                  },
                  "downlink5G": {
                    "aqDepthLog2": 4,
                    "numAqsPerGroups": 16,
                    "numQueueGroups": 0
                  },
                  "maxQueueSize": 1024,
                  "numVfBundles": 2,
                  "pfMode": false,
                  "qfft": {
                    "aqDepthLog2": 4,
                    "numAqsPerGroups": 16,
                    "numQueueGroups": 4
                  },
                  "uplink4G": {
                    "aqDepthLog2": 4,
                    "numAqsPerGroups": 16,
                    "numQueueGroups": 4
                  },
                  "uplink5G": {
                    "aqDepthLog2": 4,
                    "numAqsPerGroups": 16,
                    "numQueueGroups": 0
                  }
                }
              },
              "node": "cxlex",
              "pciAddress": "0000:f7:00.0"
            }
          ],
          "num_aal_lpus_configured": 2,
          "lpu_type": "Single",
          "aal_lpu_list":[{
              "aal_lpu_handle": "",
              "aal_lpu_image_version": "",
              "aal_lpu_image_location": "vfio-pci",
              "aal_lpu_profile_list": [{
                  "aal_lpu_profile_name": "",
                  "aal_lpu_profile_version": "",
                  "aal_lpu_profile_image_version": "",
                  "aal_lpu_profile_image_location": "",
                  "aal_lpu_profile_attributes": [],
                  "aal_lpu_profile_vendor_specific": []
                  }],
               "aal_lpu_config": {}
              }]
      }
  ]
}
```
The `hw_accel_vendor_specific` needs to have the `bbDevConfig` as defined in the Intel SRIOV-FEC Operator instructions. In addition, one needs to provide the `node` and `pciAddress` of the HW-Accel, as the backend uses these to select the HW-Accel where the config is set.

The other parameters that need to be set are `hw_accel_id`, `hw_accel_image_location`, `aal_lpu_image_location` and `num_aal_lpus_configured`. As the operator only supports one type of AAL-LPU, only one item in the `aal_lpu_list` needs to be provided, the amount of AAL-LPUs created is then determined by the `num_aal_lpus_configured` parameter.


# Future work

The operations implemented are ones which require no changes in the SRIOV-FEC Operator. Most of the operations, if not all of them could work. However, it would possibly require work in the SRIOV-FEC Operator, for example to expose fault metrics differently.
