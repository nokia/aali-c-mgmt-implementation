from utils import accel_cr_mapping, get_accel_info, get_accel_cr_status

def get_aal_accel_info(accel_ids: list):
    accel_config_status = get_accel_cr_status.get_accel_cr_status()
    accel_devices = accel_cr_mapping.get_hw_accel_list(accel_config_status)

    return_data = {
        "hw_accel_list": get_accel_info.get_accel_info(accel_devices, accel_ids).get("resources", []),
        "status_of_operation": "success"
    }
    return return_data
