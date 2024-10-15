
def aal_fault_notification(faults):
    filename = 'db/fault_log.txt'
    with open(filename, 'a') as file:
        file.write(str(faults) + "\n")
    return {
        "status_of_operation": "Success."
        }