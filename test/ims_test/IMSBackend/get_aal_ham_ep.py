
def get_aal_ham_ep():
    filename = 'ham_endpoint.txt'
    with open(filename, 'r') as file:
        ham_endpoint = file.read()
    return ham_endpoint.strip()

if __name__ == "__main__":
    print(get_aal_ham_ep())
