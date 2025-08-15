#!/usr/bin/env python3
"""
Read client for CraftLore Combined TP.
Allows querying both account and asset data from the blockchain.
"""

import base64
import hashlib
import requests
import sys
import json

REST_API_URL = "http://rest-api:8008"
# REST_API_URL = "http://localhost:8008"

# Combined TP namespace
NAMESPACE = hashlib.sha512('craftlore'.encode('utf-8')).hexdigest()[0:6]

# Account prefixes
ACCOUNT_PREFIX = '00'
EMAIL_INDEX_PREFIX = '01'
ACCOUNT_TYPE_INDEX_PREFIX = '02'
BOOTSTRAP_PREFIX = '03'

# Asset prefixes
RAW_MATERIAL_PREFIX = '10'
PRODUCT_PREFIX = '11'
PRODUCT_BATCH_PREFIX = '12'
WORK_ORDER_PREFIX = '13'
WARRANTY_PREFIX = '14'

# Index prefixes
OWNER_INDEX_PREFIX = 'f0'
ASSET_TYPE_INDEX_PREFIX = 'f1'
BATCH_INDEX_PREFIX = 'f2'

def _make_address(prefix, value):
    """Generate blockchain address."""
    value_hash = hashlib.sha512(value.encode('utf-8')).hexdigest()[0:62]
    return NAMESPACE + prefix + value_hash

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

def query_account_by_email(email):
    """Query account by email."""
    address = _make_address(EMAIL_INDEX_PREFIX, email)
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

def query_accounts_by_type(account_type):
    """Query accounts by type."""
    address = _make_address(ACCOUNT_TYPE_INDEX_PREFIX, account_type)
    data = get_state(address)
    if data:
        print(f"Accounts of type {account_type}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print(f"No accounts found of type {account_type}.")

# =============================================
# ASSET QUERIES
# =============================================

def query_asset(asset_id, asset_type):
    """Query asset by ID and type."""
    # Map asset type to prefix
    type_prefixes = {
        'raw_material': RAW_MATERIAL_PREFIX,
        'product': PRODUCT_PREFIX,
        'product_batch': PRODUCT_BATCH_PREFIX,
        'work_order': WORK_ORDER_PREFIX,
        'warranty': WARRANTY_PREFIX
    }
    
    prefix = type_prefixes.get(asset_type)
    if not prefix:
        print(f"Invalid asset type: {asset_type}")
        return
    
    address = _make_address(prefix, asset_id)
    data = get_state(address)
    if data:
        print(f"Asset {asset_id} (type: {asset_type}):")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print(f"No asset found with ID {asset_id} and type {asset_type}.")

def query_assets_by_owner(owner_public_key):
    """Query assets by owner."""
    address = _make_address(OWNER_INDEX_PREFIX, owner_public_key)
    data = get_state(address)
    if data:
        print(f"Assets owned by {owner_public_key}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print(f"No assets found for owner {owner_public_key}.")

def query_assets_by_type(asset_type):
    """Query assets by type."""
    address = _make_address(ASSET_TYPE_INDEX_PREFIX, asset_type)
    data = get_state(address)
    if data:
        print(f"Assets of type {asset_type}:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print(f"No assets found of type {asset_type}.")

# =============================================
# GENERAL QUERIES
# =============================================

def list_all_state():
    """List all state entries."""
    url = f"{REST_API_URL}/state?address={NAMESPACE}"
    resp = requests.get(url)
    state_text = ""
    if resp.status_code == 200:
        entries = resp.json().get('data', [])
        print(f"Found {len(entries)} state entries:")
        for entry in entries:
            addr = entry['address']
            data = base64.b64decode(entry['data'])
            print(f"\nAddress: {addr}")
            prefix = addr[6:8] if len(addr) >= 8 else "??"
            
            # Identify type based on prefix
            if prefix == ACCOUNT_PREFIX:
                print("Type: Account")
            elif prefix == EMAIL_INDEX_PREFIX:
                print("Type: Email Index")
            elif prefix == ACCOUNT_TYPE_INDEX_PREFIX:
                print("Type: Account Type Index")
            elif prefix == RAW_MATERIAL_PREFIX:
                print("Type: Raw Material")
            elif prefix == PRODUCT_PREFIX:
                print("Type: Product")
            elif prefix == PRODUCT_BATCH_PREFIX:
                print("Type: Product Batch")
            elif prefix == WORK_ORDER_PREFIX:
                print("Type: Work Order")
            elif prefix == WARRANTY_PREFIX:
                print("Type: Warranty")
            elif prefix == OWNER_INDEX_PREFIX:
                print("Type: Owner Index")
            elif prefix == ASSET_TYPE_INDEX_PREFIX:
                print("Type: Asset Type Index")
            else:
                print(f"Type: Unknown (prefix: {prefix})")
            
            try:
                obj = json.loads(data.decode(errors='ignore'))
                state_text += json.dumps(obj, indent=2) + "\n"
                print(json.dumps(obj, indent=2))
            except Exception:
                print(data.decode(errors='ignore'))
            print('-'*60)
            with open("state_dump.txt", "w") as f:
                f.write(state_text)
    else:
        print("Failed to fetch state entries.")

def query_bootstrap_status():
    """Query bootstrap status."""
    address = _make_address(BOOTSTRAP_PREFIX, 'bootstrap_complete')
    data = get_state(address)
    if data:
        print("Bootstrap status:")
        try:
            obj = json.loads(data.decode(errors='ignore'))
            print(json.dumps(obj, indent=4))
        except Exception:
            print(data.decode(errors='ignore'))
    else:
        print("Bootstrap not yet completed.")

def main():
    """Main interactive menu."""
    print("=" * 50)
    print("CraftLore Combined TP Read Client")
    print("=" * 50)
    
    while True:
        print("\n--- ACCOUNT QUERIES ---")
        print("1. Query Account by Public Key")
        print("2. Query Account by Email")
        print("3. Query Accounts by Type")
        print("4. Query Bootstrap Status")
        
        print("\n--- ASSET QUERIES ---")
        print("5. Query Asset by ID and Type")
        print("6. Query Assets by Owner")
        print("7. Query Assets by Type")
        
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
            
        elif choice == '3':
            print("Available account types: buyer, seller, artisan, workshop, distributor, wholesaler, retailer, verifier, admin, super_admin, supplier")
            account_type = input("Enter account type: ").strip()
            query_accounts_by_type(account_type)
            
        elif choice == '4':
            query_bootstrap_status()
            
        elif choice == '5':
            asset_id = input("Enter asset ID: ").strip()
            print("Available asset types: raw_material, product, product_batch, work_order, warranty")
            asset_type = input("Enter asset type: ").strip()
            query_asset(asset_id, asset_type)
            
        elif choice == '6':
            owner = input("Enter owner public key: ").strip()
            query_assets_by_owner(owner)
            
        elif choice == '7':
            print("Available asset types: raw_material, product, product_batch, work_order, warranty")
            asset_type = input("Enter asset type: ").strip()
            query_assets_by_type(asset_type)
            
        elif choice == '8':
            list_all_state()
            
        elif choice == '9':
            print("Goodbye!")
            break
            
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
