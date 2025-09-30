#!/usr/bin/env python3
"""
Read client for CraftLore Combined TP.
Allows querying both account and asset data from the blockchain.
"""

import base64
import hashlib
import requests
import json

from utils import SerializationHelper, CraftLoreAddressGenerator

address_generator = CraftLoreAddressGenerator()
serializer = SerializationHelper()

REST_API_URL = "http://rest-api:8008"
# REST_API_URL = "http://localhost:8008"

def get_state(address):
    """Get state data from blockchain."""
    url = f"{REST_API_URL}/state/{address}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if 'data' in data:
            return base64.b64decode(data['data'])
    return None

# =============================================
# ACCOUNT QUERIES
# =============================================

def query_account_by_public_key(pubkey):
    """Query account by public key."""
    address = address_generator.generate_account_address(pubkey)
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

def query_account_by_email(email):
    """Query account by email."""
    address = address_generator.generate_email_index_address(email)
    data = get_state(address)
    if data:
        print(f"Email index for {email}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
            # Get the actual account
            if 'public_key' in obj:
                print("\nCorresponding account:")
                query_account_by_public_key(obj['public_key'])
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print("No account found for this email.")


# =============================================
# ASSET QUERIES
# =============================================

def query_asset(asset_id):
    """Query asset by ID and type."""
    # Map asset type to prefix
    address = address_generator.generate_asset_address(asset_id)
    data = get_state(address)

    if data:
        print(f"Asset {asset_id}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print(f"No asset found with ID {asset_id}")


# =============================================
# GENERAL QUERIES
# =============================================

def list_all_state():
    """List all state entries."""
    url = f"{REST_API_URL}/state?address={address_generator.FAMILY_NAMESPACE}"
    resp = requests.get(url)
    state_text = ""
    if resp.status_code == 200:
        entries = resp.json().get('data', [])
        print(f"Found {len(entries)} state entries:")
        for entry in entries:
            addr = entry['address']
            data = base64.b64decode(entry['data'])
            print(f"\nAddress: {addr}")
            
            try:
                obj = json.loads(data.decode(errors='ignore'))
                state_text += json.dumps(obj, indent=2) + "\n"
                print(json.dumps(obj, indent=2))
            except Exception:
                print(data.decode(errors='ignore'))
            print('-'*60)
    else:
        print("Failed to fetch state entries.")

def query_transaction_by_signature(txn_sig):
    """Query transaction by signature and print decoded payload + signer pubkey."""
    url = f"{REST_API_URL}/transactions/{txn_sig}"
    resp = requests.get(url)

    if resp.status_code == 200:
        txn = resp.json().get("data", {})
        header = txn.get("header", {})
        payload_b64 = txn.get("payload", "")

        # signer public key
        signer_pubkey = header.get("signer_public_key", "N/A")

        # decode payload
        try:
            decoded = base64.b64decode(payload_b64).decode("utf-8")
            payload = json.loads(decoded)
        except Exception:
            payload = decoded  # fallback: raw string

        print("Transaction Payload (decoded):")
        print(json.dumps(payload, indent=4) if isinstance(payload, dict) else payload)
        print("\nSigner Public Key:")
        print(signer_pubkey)

    else:
        print(f"Failed to fetch transaction {txn_sig}. HTTP {resp.status_code}")

def main():
    """Main interactive menu."""
    print("=" * 50)
    print("CraftLore Combined TP Read Client")
    print("=" * 50)
    
    while True:
        print("\n--- ACCOUNT QUERIES ---")
        print("1. Query Account by Public Key")
        print("2. Query Account by Email")
        
        print("\n--- ASSET QUERIES ---")
        print("5. Query Asset by ID")
        print("6. Query Transaction by Signature")

        print("\n--- GENERAL ---")
        print("8. List All State Entries")
        print("9. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            pubkey = input("Enter public key: ").strip()
            query_account_by_public_key(pubkey)
            
        elif choice == '2':
            email = input("Enter email: ").strip()
            query_account_by_email(email)
            
        elif choice == '5':
            asset_id = input("Enter asset ID: ").strip()
            query_asset(asset_id)
            
        elif choice == '6':
            txn_sig = input("Enter transaction signature: ").strip()
            query_transaction_by_signature(txn_sig)
                    
        elif choice == '8':
            list_all_state()
            
        elif choice == '9':
            print("Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
