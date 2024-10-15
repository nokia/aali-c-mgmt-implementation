
def aal_ham_registration_notification(ham_endpoint):
    filename = 'db/ham_endpoint.txt'
    with open(filename, 'w') as file:
        file.write(ham_endpoint)
    return {
        "status_of_operation": "Success."
        }
