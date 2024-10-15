from utils import accel_cr_mapping, get_accel_cr_status

def get_aal_hw_accel_faults(accel_id: str):
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)
    status_of_operation = "failure"
    
    faults = []
    for accel_device in accel_devices:
        if accel_cr_mapping.get_hw_accel_id(accel_device) == accel_id:
            faults = accel_cr_mapping.get_hw_accel_faults(accel_device)
            for i in range(len(faults)):
                faults[i]['hw_accel_id'] = accel_cr_mapping.get_hw_accel_id(accel_device)
                faults[i]['detected_time'] = faults[i].pop("detectedTime", None)
                faults[i]['fault_id'] = faults[i].pop("faultId", None)
            # HW-Accel was found so success
            status_of_operation = "success"

    return_data = {
        "status_of_operation": status_of_operation,
        "faults": faults
        }

    return return_data
