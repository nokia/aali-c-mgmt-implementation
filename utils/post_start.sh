#!/bin/bash

# Start IMS notification scripts

cd /scripts

export PYTHONPATH="${PYTHONPATH}:/scripts/utils"

python3 backend/set_url_endpoints.py

# Run the other scripts in the background, ensuring PYTHONPATH is set for each
python3 backend/aal_ham_registration_notification_watcher.py > /var/log/aal_ham_registration_notification_watcher.log 2>&1 &
python3 backend/aal_fault_notification_watcher.py > /var/log/aal_fault_notification_watcher.log 2>&1 &
python3 backend/aal_inventory_notification_watcher.py > /var/log/aal_inventory_notification_watcher.log 2>&1 &
