#!/usr/bin/env python3

import json
import hashlib
import requests
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

def _make_hello_world_address(name):
    """Create a deterministic address for storing greetings"""
    return hashlib.sha512(
        ('hello_world' + name).encode('utf-8')
    ).hexdigest()[:70]

def create_transaction(action, name=None, private_key_hex=None):
    """Create a hello_world transaction"""
    
    # Set up cryptographic context
    context = create_context('secp256k1')
    
    if private_key_hex:
        private_key = Secp256k1PrivateKey.from_hex(private_key_hex)
    else:
        private_key = context.new_random_private_key()
        print(f"Generated Private Key: {private_key.as_hex()}")
    
    signer = CryptoFactory(context).new_signer(private_key)
    
    # Create payload
    if action == 'write':
        if not name:
            raise ValueError("Name is required for write action")
        payload_data = {'action': 'write', 'name': name}
        # For write transactions, specify input/output addresses
        address = _make_hello_world_address(name)
        inputs = [address]
        outputs = [address]
    elif action == 'read':
        payload_data = {'action': 'read'}
        # For read transactions, specify the namespace to read from
        namespace = _make_hello_world_address('')[:6]
        inputs = [namespace]
        outputs = []
    else:
        raise ValueError("Action must be 'write' or 'read'")
    
    payload_bytes = json.dumps(payload_data).encode('utf-8')
    
    # Create transaction header
    txn_header = TransactionHeader(
        family_name='hello_world',
        family_version='1.0',
        inputs=inputs,
        outputs=outputs,
        signer_public_key=signer.get_public_key().as_hex(),
        batcher_public_key=signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest()
    )
    
    txn_header_bytes = txn_header.SerializeToString()
    signature = signer.sign(txn_header_bytes)
    
    # Create transaction
    transaction = Transaction(
        header=txn_header_bytes,
        header_signature=signature,
        payload=payload_bytes
    )
    
    return transaction, signer

def create_batch(transactions, signer):
    """Create a batch from transactions"""
    
    batch_header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=[txn.header_signature for txn in transactions],
    )
    
    batch_header_bytes = batch_header.SerializeToString()
    signature = signer.sign(batch_header_bytes)
    
    batch = Batch(
        header=batch_header_bytes,
        header_signature=signature,
        transactions=transactions
    )
    
    return batch

def submit_batch(batch, rest_api_url='http://rest-api:8008'):
    """Submit a batch to the Sawtooth REST API"""
    
    batch_list = BatchList(batches=[batch])
    batch_list_bytes = batch_list.SerializeToString()
    
    try:
        response = requests.post(
            f'{rest_api_url}/batches',
            headers={'Content-Type': 'application/octet-stream'},
            data=batch_list_bytes,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        print("Transaction successfully submitted!")
        print(f"Batch ID: {result.get('link', 'N/A').split('=')[-1] if result.get('link') else 'N/A'}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to submit transaction: {e}")
        return None

def check_batch_status(batch_id, rest_api_url='http://rest-api:8008'):
    """Check the status of a batch"""
    
    try:
        response = requests.get(f'{rest_api_url}/batch_statuses?id={batch_id}')
        response.raise_for_status()
        
        result = response.json()
        batch_statuses = result.get('data', [])
        
        if batch_statuses:
            status = batch_statuses[0]
            print(f"Batch Status: {status.get('status')}")
            
            if status.get('status') == 'INVALID':
                print("Invalid transactions:")
                for txn in status.get('invalid_transactions', []):
                    print(f"  - {txn.get('message')}")
        else:
            print("Batch status not found")
            
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to check batch status: {e}")
        return None

def main():
    print("=== Hello World Sawtooth Client ===")
    
    # Get user input
    action = input("Enter action (write/read): ").strip().lower()
    
    if action not in ['write', 'read']:
        print("Invalid action. Must be 'write' or 'read'.")
        return
    
    name = None
    if action == 'write':
        name = input("Enter name: ").strip()
        if not name:
            print("Name cannot be empty for write action.")
            return
    
    # Option to use existing private key
    use_existing_key = input("Use existing private key? (y/n): ").strip().lower()
    private_key_hex = None
    if use_existing_key == 'y':
        private_key_hex = input("Enter private key (hex): ").strip()
    
    try:
        # Create transaction
        print(f"\nCreating {action} transaction...")
        transaction, signer = create_transaction(action, name, private_key_hex)
        
        # Create batch
        print("Creating batch...")
        batch = create_batch([transaction], signer)
        
        # Submit batch
        print("Submitting batch...")
        result = submit_batch(batch)
        
        if result and result.get('link'):
            # Extract batch ID and check status
            batch_id = result['link'].split('=')[-1]
            print(f"\nChecking batch status...")
            check_batch_status(batch_id)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
