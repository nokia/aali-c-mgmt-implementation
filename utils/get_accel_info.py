from utils import accel_cr_mapping

def get_accel_info(accel_devices: list, accel_ids: list = None):
    return_data = {}
    return_data["resources"] = []
    if accel_ids == None:
        for accel_device in accel_devices:
            return_data["resources"].append(accel_cr_mapping.accel_cr_mapping(accel_device))
    else:
        for accel_id in accel_ids:
            accel_device_list = [accel_device for accel_device in accel_devices if accel_cr_mapping.get_hw_accel_id(accel_device) == accel_id]
            if len(accel_device_list) > 0:
                accel_device = accel_device_list[0]
                return_data["resources"].append(accel_cr_mapping.accel_cr_mapping(accel_device))
    return return_data
