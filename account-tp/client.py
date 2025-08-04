#!/usr/bin/env python3

import json
import time
import hashlib
import requests
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_signing import create_context, CryptoFactory


class CraftloreAccountTPClient:
    """Client for Craftlore Account Transaction Processor."""
    
    def __init__(self, base_url='http://rest-api:8008'):
        self.base_url = base_url
        self.context = create_context('secp256k1')
        self.crypto_factory = CryptoFactory(self.context)
        
        # Generate a private key for this client session
        self.private_key = self.context.new_random_private_key()
        self.signer = self.crypto_factory.new_signer(self.private_key)
        self.public_key = self.signer.get_public_key().as_hex()
        
        print(f"Craftlore Account TP Client initialized")
        print(f"Public Key: {self.public_key}")
    
    def _get_namespace(self):
        """Get the 6-character namespace."""
        return hashlib.sha512('craftlore-account'.encode()).hexdigest()[:6]
    
    def _get_address(self, key):
        """Generate a 70-character address from a key."""
        namespace = self._get_namespace()
        return namespace + hashlib.sha512(key.encode()).hexdigest()[:64]
    
    def set_value(self, key, value):
        """Set a key-value pair."""
        payload = {
            'action': 'set',
            'key': key,
            'value': value
        }
        return self._submit_transaction(payload, key)
    
    def get_value(self, key):
        """Get a value by key."""
        payload = {
            'action': 'get',
            'key': key
        }
        return self._submit_transaction(payload, key)
    
    def delete_value(self, key):
        """Delete a key-value pair."""
        payload = {
            'action': 'delete',
            'key': key
        }
        return self._submit_transaction(payload, key)
    
    def _submit_transaction(self, payload, key):
        """Submit a transaction."""
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Generate address for this key
        address = self._get_address(key)
        
        # Create transaction header
        txn_header = TransactionHeader(
            family_name='craftlore-account',
            family_version='1.0',
            inputs=[address],
            outputs=[address],
            signer_public_key=self.public_key,
            batcher_public_key=self.public_key,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
            nonce=str(time.time())
        )
        
        # Sign transaction
        txn_header_bytes = txn_header.SerializeToString()
        signature = self.signer.sign(txn_header_bytes)
        
        # Create transaction
        transaction = Transaction(
            header=txn_header_bytes,
            header_signature=signature,
            payload=payload_bytes
        )
        
        # Create batch
        batch_header = BatchHeader(
            signer_public_key=self.public_key,
            transaction_ids=[transaction.header_signature]
        )
        
        batch_header_bytes = batch_header.SerializeToString()
        batch_signature = self.signer.sign(batch_header_bytes)
        
        batch = Batch(
            header=batch_header_bytes,
            header_signature=batch_signature,
            transactions=[transaction]
        )
        
        # Create batch list
        batch_list = BatchList(batches=[batch])
        
        # Submit to REST API
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(
            f"{self.base_url}/batches",
            data=batch_list.SerializeToString(),
            headers=headers
        )
        
        if response.status_code == 202:
            batch_id = batch.header_signature
            return self._wait_for_batch_commit(batch_id)
        else:
            return {
                'status': 'error',
                'message': f'Failed to submit batch: {response.status_code}',
                'details': response.text
            }
    
    def _wait_for_batch_commit(self, batch_id, timeout=30):
        """Wait for batch to be committed."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/batch_statuses?id={batch_id}")
                
                if response.status_code == 200:
                    batch_status = response.json()
                    
                    if 'data' in batch_status and len(batch_status['data']) > 0:
                        status = batch_status['data'][0]['status']
                        
                        if status == 'COMMITTED':
                            return {
                                'status': 'success',
                                'batch_id': batch_id,
                                'message': 'Transaction committed successfully'
                            }
                        elif status in ['INVALID', 'UNKNOWN']:
                            return {
                                'status': 'error',
                                'batch_id': batch_id,
                                'message': f'Transaction failed with status: {status}',
                                'details': batch_status['data'][0].get('invalid_transactions', [])
                            }
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error checking batch status: {e}")
                time.sleep(1)
        
        return {
            'status': 'timeout',
            'batch_id': batch_id,
            'message': 'Transaction timed out'
        }


def main():
    """Test the craftlore account transaction processor."""
    print("🚀 Craftlore Account TP Client Test")
    print("=" * 30)

    client = CraftloreAccountTPClient()

    try:
        # Test 1: Set a value
        print("\n📝 Test 1: Set value")
        result = client.set_value('test_key', 'hello_world')
        print(f"Result: {result}")
        
        # Test 2: Get the value
        print("\n📖 Test 2: Get value")
        result = client.get_value('test_key')
        print(f"Result: {result}")
        
        # Test 3: Set another value
        print("\n📝 Test 3: Set another value")
        result = client.set_value('counter', '42')
        print(f"Result: {result}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
