
def aal_inventory_notification(inventory):
    filename = 'db/inventory.txt'
    with open(filename, 'a') as file:
        file.write(str(inventory))
    return {
        "status_of_operation": "Success."
        }
