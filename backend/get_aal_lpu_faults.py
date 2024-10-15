
from utils import accel_cr_mapping, get_accel_cr_status

def get_aal_lpu_faults(accel_ids: list, lpu_handle: str):
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)

    status_of_operation = "failure"
    faults = []
    for accel_device in accel_devices:
        if accel_cr_mapping.get_hw_accel_id(accel_device) in accel_ids:
            for lpu in accel_cr_mapping.get_hw_accel_lpus(accel_device):
                if accel_cr_mapping.get_lpu_handle(lpu) == lpu_handle:
                    faults = accel_cr_mapping.get_lpu_faults(lpu)
                    for i in range(len(faults)):
                        faults[i]['hw_accel_id'] = accel_cr_mapping.get_hw_accel_id(accel_device)
                        faults[i]['aal_lpu_handle'] = accel_cr_mapping.get_lpu_handle(lpu)
                        faults[i]['detected_time'] = faults[i].pop("detectedTime", None)
                        faults[i]['fault_id'] = faults[i].pop("faultId", None)
                    # LPU was found so success
                    status_of_operation = "success"
    

    return_data = {
        "status_of_operation": status_of_operation,
        "faults": faults
        }

    return return_data