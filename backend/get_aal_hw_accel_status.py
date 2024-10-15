from utils import accel_cr_mapping, get_accel_info, get_accel_cr_status

def get_aal_hw_accel_status(accel_id: str):
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)
    accel_device_mapped = get_accel_info.get_accel_info(accel_devices, [accel_id]).get("resources", [{}])[0]
    
    hw_accel_operational_state = accel_device_mapped.get('hw_accel_operational_state', "")
    hw_accel_operational_conditions = accel_device_mapped.get('hw_accel_operational_conditions', [])

    if hw_accel_operational_state != "":
        status_of_operation = "success"
    else:
        status_of_operation = "failure"

    return_data = {
        "hw_accel_operational_state": hw_accel_operational_state,
        "hw_accel_operational_conditions": hw_accel_operational_conditions,
        "status_of_operation": status_of_operation
        }

    return return_data

if __name__ == "__main__":
    print(get_aal_hw_accel_status("Unknown"))
