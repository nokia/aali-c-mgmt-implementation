from pydantic import BaseModel

class HWAccelID(BaseModel):
    hw_accel_id: str

class AalLpuHandle(BaseModel):
    aal_lpu_handle: str

class LpuStatus(BaseModel):
    aal_lpu_handle: str
    hw_accel_id: list[str]

class Lpu(BaseModel):
    aal_lpu_handle: str
    hw_accel_id: str

class HWAccelIDs(BaseModel):
    hw_accel_id: list[str]

class AalAccelIdentifier(BaseModel):
    vendor_name: str
    model: str
    serial_number: str
    hw_accel_id: str

class Subscription(BaseModel):
    subscription_id: str
    filter_criteria: str

class FaultSubscriptions(BaseModel):
    subscriptions: list[Subscription]

class SubscriptionIds(BaseModel):
    subscription_id: list[str]

class AalLpuConfig(BaseModel):
    aal_lpu_memory: int | None = None
    aal_lpu_multiprocessors_num: int | None = None
    aal_lpu_compute_slices_num: int | None = None
    aal_lpu_vendor_specific: list[dict] | None = None

class AalLpuProfile(BaseModel):
    aal_lpu_profile_name: str
    aal_lpu_profile_version: str
    aal_lpu_profile_image_version: str
    aal_lpu_profile_image_location: str
    aal_lpu_profile_attributes: list[dict] | None = None
    aal_lpu_profile_vendor_specific: list[dict] | None = None

class AalLpu(BaseModel):
    aal_lpu_handle: str
    aal_lpu_image_location: str
    aal_lpu_image_version: str
    aal_lpu_profile_list: list[AalLpuProfile] | None = None
    aal_lpu_config: AalLpuConfig | None = None

class AalAccelConfig(BaseModel):
    hw_accel_id: str
    hw_accel_image_location: str
    hw_accel_image_version: str
    num_aal_lpus_configured: int
    lpu_type: str
    hw_accel_vendor_specific: list[dict] | None = None
    aal_lpu_list: list[AalLpu] | None = None

class AalAccelsConfig(BaseModel):
    hw_accel_list: list[AalAccelConfig]
