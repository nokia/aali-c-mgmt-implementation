

def accel_cr_mapping(accel_device: dict):
    return {
        "hw_accel_id": accel_device.get('hwAccelId', ""),
        "hw_accel_operational_state": accel_device.get('operationalState', ""),
        "hw_accel_operational_conditions": accel_device.get('operationalConditions', []),
        "vendor_name": accel_device.get('vendorName', ""),
        "date_of_manufacture": accel_device.get('dateOfManufacture', ""),
        "model": accel_device.get('model', ""),
        "serial_number": accel_device.get('serialNum', ""),
        "hw_version": accel_device.get('hwVersion', ""),
        "hw_accel_image_version": accel_device.get('imageVersion', ""),
        "hw_accel_image_location": accel_device.get('imageLocation', ""),
        "hw_accel_vendor_specific": accel_device.get('extensions', ""),
        "max_num_aal_lpus": accel_device.get('maxNumAalLpus', None),
        "aal_profile_templates": get_aal_templates(accel_device.get('aalProfileTemplates', [])),
        "num_aal_lpus_configured": accel_device.get('numAalLpusConfigured', None),
        "lpu_type": accel_device.get('lpuType', ""),
        "aal_lpu_list": get_aal_lpus(accel_device.get('aalLpu', []))
    }

def get_aal_templates(templates: list):
    mapped_templates = []
    for template in templates:
        mapped_template = {
            "name": template.get('name', ""),
            "version": template.get('version', ""),
            "imageVersion": template.get('imageVersion', ""),
            "attributes": template.get('attributes', []),
            "extensions": template.get('extensions', []),
            "capabilities": template.get('capabilities', [])
        }
        mapped_templates.append(mapped_template)
    return mapped_templates

def get_aal_lpus(lpus: list):
    mapped_lpus = []
    for lpu in lpus:
        mapped_lpu = {
            "aal_lpu_handle": lpu.get('aalLpuHandle', ""),
            "aal_lpu_administrative_state": lpu.get('administrativeState', ""),
            "aal_lpu_operational_state": lpu.get('operationalState', ""),
            "aal_lpu_operational_conditions": lpu.get('operationalConditions', []),
            "aal_lpu_image_version": lpu.get('imageVersion', ""),
            "aal_lpu_image_location": lpu.get('imageLocation', ""),
            "aal_lpu_profile_list": get_aal_profiles(lpu.get('supportedAalProfiles', [])),
            "aal_lpu_config": {
                "aal_lpu_memory": lpu.get('aal_lpu_config', {}).get('memory', None),
                "aal_lpu_multiprocessors_num": lpu.get('aal_lpu_config', {}).get('multiprocessorNum', None),
                "aal_lpu_compute_slices_num": lpu.get('aal_lpu_config', {}).get('computeSlicesNum', None),
                "aal_lpu_vendor_specific": lpu.get('aal_lpu_config', {}).get('extensions', [])
            },
            "aal_lpu_vendor_specific": lpu.get('extensions', [])
        }
        mapped_lpus.append(mapped_lpu)
    return mapped_lpus

def get_aal_profiles(profiles: list):
    mapped_profiles = []
    for profile in profiles:
        mapped_profile = {
            "aal_lpu_profile_name": profile.get('name', ""),
            "aal_lpu_profile_version": profile.get('version', ""),
            "aal_lpu_profile_image_version": profile.get('imageVersion', ""),
            "aal_lpu_profile_image_location": profile.get('imageLocation', ""),
            "aal_lpu_profile_attributes": profile.get('attributes', []),
            "aal_lpu_profile_vendor_specific": profile.get('extensions', [])
        }
        mapped_profiles.append(mapped_profile)
    return mapped_profiles

def get_hw_accel_id(accel_device: dict):
    return accel_device.get('hwAccelId', "")

def get_hw_accel_operational_state(accel_device: dict):
    return accel_device.get('operationalState', "")

def get_hw_accel_operational_conditions(accel_device: dict):
    return accel_device.get('operationalConditions', [])

def get_hw_accel_list(accel_cr_status: dict):
    return accel_cr_status.get('hwAccelList', [])

def get_hw_accel_faults(accel_device: dict):
    return accel_device.get('faults', [])

def get_hw_accel_lpus(accel_device: dict):
    return accel_device.get('aalLpu', [])

def get_hw_accel_model(accel_device: dict):
    return accel_device.get('model', "")

def get_hw_accel_serial_number(accel_device: dict):
    return accel_device.get('serialNum', "")

def get_hw_accel_vendor_name(accel_device: dict):
    return accel_device.get('vendorName', "")

def get_lpu_faults(lpu: dict):
    return lpu.get('faults', [])

def get_lpu_id(lpu: dict):
    return lpu.get('aalLpuId', "")

def get_lpu_handle(lpu: dict):
    return lpu.get('aalLpuHandle', "")

def get_lpu_operational_state(lpu: dict):
    return lpu.get('operationalState', "")

def get_lpu_operational_conditions(lpu: dict):
    return lpu.get('operationalConditions', [])

def get_ims_url(accel_cr_status: dict):
    return accel_cr_status.get("aalHam", {}).get("registrationServiceEndpoint", "")

def get_aal_ham_info(accel_cr_status: dict):
    return {
        "operationalState": accel_cr_status.get('aalHam', {}).get('operationalState', ""),
        "imsRegistrationState": accel_cr_status.get('aalHam', {}).get('imsRegistrationState', ""),
        "localServiceEndpoint": accel_cr_status.get('aalHam', {}).get('localServiceEndpoint', ""),
        "registrationServiceEndpoint": accel_cr_status.get('aalHam', {}).get('registrationServiceEndpoint', "")
    }

def set_hw_accel_cr_mapping(new_config: dict):
    return {
        "hwAccelId": new_config.get('hw_accel_id', ""),
        "imageVersion": new_config.get('hw_accel_image_version', ""),
        "imageLocation": new_config.get('hw_accel_image_location', ""),
        "extensions": new_config.get('hw_accel_vendor_specific', []),
        "numAalLpusConfigured": new_config.get('num_aal_lpus_configured', None),
        "lpuType": new_config.get('lpu_type', ""),
        "aalLpu": set_aal_lpus(new_config.get('aal_lpu_list', []))
    }

def set_aal_lpus(lpus: list):
    mapped_lpus = []
    for lpu in lpus:
        mapped_lpu = {
            "aalLpuHandle": lpu.get('aal_lpu_handle', ""),
            "imageVersion": lpu.get('aal_lpu_image_version', ""),
            "imageLocation": lpu.get('aal_lpu_image_location', ""),
            "supportedAalProfiles": set_aal_profiles(lpu.get('aal_lpu_profile_list', [])),
            "aalLpuConfig": {
                "memory": lpu.get('aal_lpu_config', {}).get('aal_lpu_memory', None),
                "multiprocessorNum": lpu.get('aal_lpu_config', {}).get('aal_lpu_multiprocessors_num', None),
                "computeSlicesNum": lpu.get('aal_lpu_config', {}).get('aal_lpu_compute_slices_num', None),
                "extensions": lpu.get('aal_lpu_config', {}).get('aal_lpu_vendor_specific', [])
            }
        }
        mapped_lpus.append(mapped_lpu)
    return mapped_lpus

def set_aal_profiles(profiles: list):
    mapped_profiles = []
    for profile in profiles:
        mapped_profile = {
            "name": profile.get('aal_lpu_profile_name', ""),
            "version": profile.get('aal_lpu_profile_version', ""),
            "imageVersion": profile.get('aal_lpu_profile_image_version', ""),
            "imageLocation": profile.get('aal_lpu_profile_image_location', ""),
            "attributes": profile.get('aal_lpu_profile_attributes', []),
            "extensions": profile.get('aal_lpu_profile_vendor_specific', [])
        }
        mapped_profiles.append(mapped_profile)
    return mapped_profiles
