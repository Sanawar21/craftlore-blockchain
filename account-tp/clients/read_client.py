import base64
import hashlib
import requests
import sys
import json

REST_API_URL = "http://localhost:8008"
NAMESPACE = hashlib.sha512('craftlore-account'.encode('utf-8')).hexdigest()[0:6]
ACCOUNT_PREFIX = '00'
EMAIL_PREFIX = '01'

def _make_address(prefix, value):
    value_hash = hashlib.sha512(value.encode('utf-8')).hexdigest()[0:62]
    return NAMESPACE + prefix + value_hash

def get_state(address):
    url = f"{REST_API_URL}/state/{address}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data:
            return base64.b64decode(data['data'])
    return None

def query_by_public_key(pubkey):
    address = _make_address(ACCOUNT_PREFIX, pubkey)
    data = get_state(address)
    if data:
        print(f"Account for public key {pubkey}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print("No account found for this public key.")

def query_by_email(email):
    address = _make_address(EMAIL_PREFIX, email)
    data = get_state(address)
    if data:
        print(f"Account for email {email}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print("No account found for this email.")


def list_all_accounts():
    url = f"{REST_API_URL}/state?address={NAMESPACE}"
    resp = requests.get(url)
    if resp.status_code == 200:
        entries = resp.json().get('data', [])
        for entry in entries:
            addr = entry['address']
            data = base64.b64decode(entry['data'])
            print(f"Address: {addr}")
            try:
                obj = json.loads(data.decode(errors='ignore'))
                print(json.dumps(obj, indent=4))
            except Exception:
                print(data.decode(errors='ignore'))
            print('-'*40)
    else:
        print("Failed to fetch state entries.")

def main():
    print("Account Read Client")
    print("1. Query by Public Key")
    print("2. Query by Email")
    print("3. List All Accounts")
    choice = input("Select option: ")
    if choice == '1':
        pubkey = input("Enter public key: ")
        query_by_public_key(pubkey)
    elif choice == '2':
        email = input("Enter email: ")
        query_by_email(email)
    elif choice == '3':
        list_all_accounts()
    else:
        print("Invalid option.")

if __name__ == "__main__":
    main()
