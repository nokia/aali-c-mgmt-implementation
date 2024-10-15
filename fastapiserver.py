from fastapi import FastAPI
from backend import get_aal_hw_accel_status, get_aal_accel_info, get_aal_fault_subscription, get_aal_hw_accel_faults, get_aal_lpu_faults, get_aal_lpu_status, set_aal_accel_config, set_aal_accel_identifier, start_aal_lpu,stop_aal_lpu, create_aal_fault_subscription, delete_aal_fault_subscription
from backend import request_schemas, response_schemas

app = FastAPI()
  
@app.post('/getAalHwAccelStatus', response_model=response_schemas.GetAalHwAccelStatus)
def GetAalHwAccelStatus(hwAccelID: request_schemas.HWAccelID):
    data = get_aal_hw_accel_status.get_aal_hw_accel_status(hwAccelID.hw_accel_id)
    return data

@app.post('/getAalLpuStatus', response_model=response_schemas.GetAalLpuStatus) 
def GetAalLpuStatus(lpuStatus: request_schemas.LpuStatus):
    data = get_aal_lpu_status.get_aal_lpu_status(lpuStatus.hw_accel_id, lpuStatus.aal_lpu_handle)
    return data

@app.post('/getAalAccelInfo', response_model=response_schemas.GetAalAccelInfo)
def GetAalAccelInfo(hwAccelIDs: request_schemas.HWAccelIDs):
    data = get_aal_accel_info.get_aal_accel_info(hwAccelIDs.hw_accel_id)
    return data
    
@app.post('/setAalAccelConfig', response_model=response_schemas.SetAalAccelConfig) 
def SetAalAccelConfig(aalAccelsConfig: request_schemas.AalAccelsConfig): 
    data = set_aal_accel_config.set_aal_accel_config(aalAccelsConfig.model_dump().get("hw_accel_list", []))
    return data

@app.post('/setAalAccelIdentifier', response_model=response_schemas.SetAalAccelIdentifier) 
def SetAalAccelIdentifier(aalAccelIdentifier: request_schemas.AalAccelIdentifier): 
    data = set_aal_accel_identifier.set_aal_accel_identifier(aalAccelIdentifier.vendor_name, aalAccelIdentifier.model, aalAccelIdentifier.serial_number, aalAccelIdentifier.hw_accel_id)
    return data
    
@app.post('/getAalHwAccelFaults', response_model=response_schemas.GetAalHwAccelFaults) 
def GetAalHwAccelFaults(hwAccelID: request_schemas.HWAccelID): 
    data = get_aal_hw_accel_faults.get_aal_hw_accel_faults(hwAccelID.hw_accel_id)
    return data
    
@app.post('/getAalLpuFaults', response_model=response_schemas.GetAalLpuFaults) 
def GetAalLpuFaults(lpuStatus: request_schemas.LpuStatus): 
    data = get_aal_lpu_faults.get_aal_lpu_faults(lpuStatus.hw_accel_id, lpuStatus.aal_lpu_handle)
    return data
    
@app.post('/createAalFaultSubscription', response_model=response_schemas.CreateAalFaultSubscription) 
def CreateAalFaultSubscription(faultSubscriptions: request_schemas.FaultSubscriptions): 
    data = create_aal_fault_subscription.create_aal_fault_subscription(faultSubscriptions.model_dump().get("subscriptions", []))
    return data
    
@app.post('/deleteAalFaultSubscription', response_model=response_schemas.DeleteAalFaultSubscription) 
def DeleteAalFaultSubscription(subscriptions: request_schemas.SubscriptionIds): 
    data = delete_aal_fault_subscription.delete_aal_fault_subscription(subscriptions.model_dump().get("subscription_id", []))
    return data

@app.post('/getAalFaultSubscription', response_model=response_schemas.GetAalFaultSubscription) 
def GetAalFaultSubscription(subscriptions: request_schemas.SubscriptionIds): 
    data = get_aal_fault_subscription.get_aal_fault_subscription(subscriptions.model_dump().get("subscription_id", []))
    return data

@app.get('/getAalFaultSubscription', response_model=response_schemas.GetAalFaultSubscription) 
def GetAalFaultSubscription(): 
    data = get_aal_fault_subscription.get_aal_fault_subscription()
    return data
    
@app.post('/startAalLpu', response_model=response_schemas.StartAalLpu) 
def StartAalLpu(lpu: request_schemas.Lpu): 
    data = start_aal_lpu.start_aal_lpu(lpu.hw_accel_id, lpu.aal_lpu_handle)
    return data
    
@app.post('/stopAalLpu', response_model=response_schemas.StopAalLpu) 
def StopAalLpu(lpu: request_schemas.Lpu): 
    data = stop_aal_lpu.stop_aal_lpu(lpu.hw_accel_id, lpu.aal_lpu_handle)
    return data

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
