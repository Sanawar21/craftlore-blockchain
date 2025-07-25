#!/usr/bin/env python3

import json
import hashlib
import requests
import time
import base64
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

def _make_hello_world_address(name):
    """Create a deterministic address for storing greetings"""
    return hashlib.sha512(
        ('hello_world' + name).encode('utf-8')
    ).hexdigest()[:70]

def test_hello_world():
    """Test a simple hello world transaction"""
    
    print("=== Testing Hello World Transaction ===")
    
    # Set up cryptographic context
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    signer = CryptoFactory(context).new_signer(private_key)
    
    print(f"Private Key: {private_key.as_hex()}")
    print(f"Public Key: {signer.get_public_key().as_hex()}")
    
    # Create write payload
    name = "Sanawar"
    payload_data = {'action': 'write', 'name': name}
    payload_bytes = json.dumps(payload_data).encode('utf-8')
    
    # Address for storage
    address = _make_hello_world_address(name)
    print(f"Storage Address: {address}")
    
    # Create transaction header
    txn_header = TransactionHeader(
        family_name='hello_world',
        family_version='1.0',
        inputs=[address],
        outputs=[address],
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
    
    print(f"Transaction ID: {transaction.header_signature}")
    
    # Create batch
    batch_header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature],
    )
    
    batch_header_bytes = batch_header.SerializeToString()
    batch_signature = signer.sign(batch_header_bytes)
    
    batch = Batch(
        header=batch_header_bytes,
        header_signature=batch_signature,
        transactions=[transaction]
    )
    
    print(f"Batch ID: {batch.header_signature}")
    
    # Submit batch
    batch_list = BatchList(batches=[batch])
    batch_list_bytes = batch_list.SerializeToString()
    
    try:
        print("\nSubmitting transaction...")
        response = requests.post(
            'http://rest-api:8008/batches',
            headers={'Content-Type': 'application/octet-stream'},
            data=batch_list_bytes,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        print("✅ Transaction submitted successfully!")
        print(f"Response: {result}")
        
        # Wait and check status
        print("\nWaiting for processing...")
        time.sleep(3)
        
        status_response = requests.get(f'http://rest-api:8008/batch_statuses?id={batch.header_signature}')
        if status_response.status_code == 200:
            status_result = status_response.json()
            print(f"Batch Status: {status_result}")
            
            batch_status = status_result.get('data', [{}])[0].get('status', 'UNKNOWN')
            if batch_status == 'COMMITTED':
                print("✅ Transaction committed successfully!")
                
                # Check state
                print("\nChecking state...")
                state_response = requests.get(f'http://rest-api:8008/state/{address}')
                if state_response.status_code == 200:
                    state_data = state_response.json()
                    stored_data = json.loads(base64.b64decode(state_data['data']).decode('utf-8'))
                    print(f"✅ Stored data: {stored_data}")
                else:
                    print("❌ Could not retrieve state")
            else:
                print(f"❌ Transaction status: {batch_status}")
        else:
            print("❌ Could not check batch status")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_hello_world()
