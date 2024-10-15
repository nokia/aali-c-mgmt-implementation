from pydantic import BaseModel

class GetAalHwAccelStatus(BaseModel):
    hw_accel_operational_state: str
    hw_accel_operational_conditions: list
    status_of_operation: str

class GetAalLpuStatusHwAccelList(BaseModel):
    hw_accel_id : str
    aal_lpu_handle: str
    aal_lpu_operational_state: str
    aal_lpu_operational_conditions: list

class GetAalLpuStatus(BaseModel):
    hw_accel_list: list[GetAalLpuStatusHwAccelList]
    status_of_operation: str

class GetAalAccelInfoHwAccelListAalProfileTemplates(BaseModel):
    name: str
    version: str
    imageVersion: str
    attributes: list
    extensions: list
    capabilities: list

class GetAalAccelInfoHwAccelListAalLpuListAalLpuProfileList(BaseModel):
    aal_lpu_profile_name: str
    aal_lpu_profile_version: str
    aal_lpu_profile_image_version: str
    aal_lpu_profile_image_location: str
    aal_lpu_profile_attributes: list[dict] | None = None
    aal_lpu_profile_vendor_specific: list[dict] | None = None

class GetAalAccelInfoHwAccelListAalLpuListAalLpuConfig(BaseModel):
    aal_lpu_memory: int | None = None
    aal_lpu_multiprocessors_num: int | None = None
    aal_lpu_compute_slices_num: int | None = None
    aal_lpu_vendor_specific: list[dict]

class GetAalAccelInfoHwAccelListAalLpuList(BaseModel):
    aal_lpu_handle: str
    aal_lpu_administrative_state: str
    aal_lpu_operational_state: str
    aal_lpu_operational_conditions: list
    aal_lpu_image_version: str
    aal_lpu_image_location: str
    aal_lpu_profile_list: list[GetAalAccelInfoHwAccelListAalLpuListAalLpuProfileList] | None = None
    aal_lpu_config: GetAalAccelInfoHwAccelListAalLpuListAalLpuConfig| None = None

class GetAalAccelInfoHwAccelList(BaseModel):
    hw_accel_id: str
    hw_accel_operational_state: str
    hw_accel_operational_conditions: list
    vendor_name: str
    date_of_manufacture: str
    model: str
    serial_number: str
    hw_version: str
    hw_accel_image_location: str
    hw_accel_image_version: str
    max_num_aal_lpus: int | None = None
    aal_profile_templates: list[GetAalAccelInfoHwAccelListAalProfileTemplates]
    num_aal_lpus_configured: int
    lpu_type: str
    aal_lpu_list: list[GetAalAccelInfoHwAccelListAalLpuList] | None = None
    hw_accel_vendor_specific: list[dict] | None = None

class GetAalAccelInfo(BaseModel):
    hw_accel_list: list[GetAalAccelInfoHwAccelList]
    status_of_operation: str

class SetAalAccelConfig(BaseModel):
    status_of_operation: str

class SetAalAccelIdentifier(BaseModel):
    status_of_operation: str

class GetAalHwAccelFaultsFaults(BaseModel):
    hw_accel_id: str
    detected_time: str
    fault_id: str

class GetAalHwAccelFaults(BaseModel):
    faults: list[GetAalHwAccelFaultsFaults]
    status_of_operation: str

class GetAalLpuFaultsFaults(BaseModel):
    hw_accel_id: str
    aal_lpu_handle: str
    detected_time: str
    fault_id: str
    
class GetAalLpuFaults(BaseModel):
    faults: list[GetAalLpuFaultsFaults]
    status_of_operation: str

class CreateAalFaultSubscriptionSubscriptions(BaseModel):
    subscription_id: str
    status_of_operation: str

class CreateAalFaultSubscription(BaseModel):
    subscriptions: list[CreateAalFaultSubscriptionSubscriptions]

class DeleteAalFaultSubscriptionSubscriptions(BaseModel):
    subscription_id: str
    status_of_operation: str

class DeleteAalFaultSubscription(BaseModel):
    subscriptions: list[DeleteAalFaultSubscriptionSubscriptions]

class GetAalFaultSubscriptionSubscriptions(BaseModel):
    subscription_id: str
    filter_criteria: str
    status_of_operation: str

class GetAalFaultSubscription(BaseModel):
    subscriptions: list[GetAalFaultSubscriptionSubscriptions]

class StartAalLpu(BaseModel):
    status_of_operation: str

class StopAalLpu(BaseModel):
    status_of_operation: str
