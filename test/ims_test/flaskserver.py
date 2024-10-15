from flask import Flask, jsonify, request
import requests
from pydantic import BaseModel
from IMSBackend import get_aal_ham_ep, aal_ham_registration_notification, aal_fault_notification, aal_inventory_notification

class AalHamEndpoint(BaseModel):
    aalHam_ep: str

class FaultInfo(BaseModel):
    hw_accel_id: str
    aal_lpu_handle: str | None = None
    detected_time: str
    event: str
    fault_id: str

class AalFaultNotificationParams(BaseModel):
    subscription_id: str
    faults: list[FaultInfo]

app = Flask(__name__)
  
@app.route('/aalHamRegistrationNotification', methods = ['POST']) 
def AalHamRegistrationNotification():
    if(request.method == 'POST'):
        try:
            data = request.json
            aalHamEndpoint = AalHamEndpoint(**data)
            data = aal_ham_registration_notification.aal_ham_registration_notification(aalHamEndpoint.aalHam_ep)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
@app.route('/hamAPI/<operation>', methods = ['GET', 'POST']) 
def QueryAalCMgmt(operation):
    url = get_aal_ham_ep.get_aal_ham_ep() + "/" + operation
    if (request.method == 'POST'):
        data = request.get_json()
        response = requests.post(url, json=data).json()
    elif (request.method == 'GET'):
        response = requests.get(url).json()
    
    return jsonify(response)

@app.route('/aalFaultNotification', methods = ['POST']) 
def AalFaultNotification():
    try:
        data = request.json
        aalFaultNotification = AalFaultNotificationParams(**data)
        data = aal_fault_notification.aal_fault_notification(aalFaultNotification.model_dump())
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/aalInventoryNotification', methods = ['POST']) 
def AalInventoryNotification():
    try:
        data = request.get_json()
        data = aal_inventory_notification.aal_inventory_notification(data)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
