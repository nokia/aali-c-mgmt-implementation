from utils import accel_cr_mapping, get_accel_cr_status

def get_aal_lpu_status(accel_ids: list, lpu_handle: str):
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)

    return_data = {}
    return_data["hw_accel_list"] = []
    for accel_device in accel_devices:
        if accel_cr_mapping.get_hw_accel_id(accel_device) in accel_ids:
            for lpu in accel_cr_mapping.get_hw_accel_lpus(accel_device):
                if accel_cr_mapping.get_lpu_handle(lpu) == lpu_handle:
                    return_data["hw_accel_list"].append({
                        "hw_accel_id": accel_cr_mapping.get_hw_accel_id(accel_device),
                        "aal_lpu_handle": accel_cr_mapping.get_lpu_handle(lpu),
                        "aal_lpu_operational_state": accel_cr_mapping.get_lpu_operational_state(lpu),
                        "aal_lpu_operational_conditions": accel_cr_mapping.get_lpu_operational_conditions(lpu)
                    })

    status_of_operation = "success"

    return_data = {
        "hw_accel_list": return_data["hw_accel_list"],
        "status_of_operation": status_of_operation
        }

    return return_data