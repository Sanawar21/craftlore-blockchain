#!/usr/bin/env python3
"""
CraftLore Account TP Client
Client for interacting with the CraftLore Account Transaction Processor.
"""

import json
import time
import hashlib
import requests
from utils.serialization import SerializationHelper
from typing import Dict, Optional
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


class AccountTPClient:
    """Client for CraftLore Account Transaction Processor."""
    
    def __init__(self, base_url: str = 'http://rest-api:8008'):
        self.base_url = base_url
        self.context = create_context('secp256k1')
        self.crypto_factory = CryptoFactory(self.context)
        self.serializer = SerializationHelper()
        
        # Generate a private key for this client session
        self.private_key = self.context.new_random_private_key()
        self.signer = self.crypto_factory.new_signer(self.private_key)
        self.public_key = self.signer.get_public_key().as_hex()
        
        
        print(f"Client initialized with public key: {self.public_key}")
        print(f"Client private key: {self.private_key.as_hex()} (keep it secret!)")

    def create_account(self, account_type: str, email: str, **kwargs) -> Dict:
        """Create a new account."""
        payload = {
            'action': 'account_create',
            'account_type': account_type,
            'email': email,
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def authenticate_account(self, target_public_key: str, auth_decision: str) -> Dict:
        """Authenticate an account (approve/reject)."""
        payload = {
            'action': 'account_authenticate',
            'target_public_key': target_public_key,
            'auth_decision': auth_decision
        }
        
        return self._submit_transaction(payload)
    
    def update_account(self, target_public_key: str = None, **updates) -> Dict:
        """Update account information."""
        payload = {
            'action': 'account_update',
            **updates
        }
        
        if target_public_key:
            payload['target_public_key'] = target_public_key
        
        return self._submit_transaction(payload)
    
    def deactivate_account(self, target_public_key: str) -> Dict:
        """Deactivate an account."""
        payload = {
            'action': 'account_deactivate',
            'target_public_key': target_public_key
        }
        
        return self._submit_transaction(payload)
    
    def query_account_by_public_key(self, public_key: str = None) -> Dict:
        """Query account by public key."""
        payload = {
            'action': 'account_query',
            'query_type': 'by_public_key'
        }
        
        if public_key:
            payload['public_key'] = public_key
        
        return self._submit_transaction(payload)
    
    def query_account_by_email(self, email: str) -> Dict:
        """Query account by email."""
        payload = {
            'action': 'account_query',
            'query_type': 'by_email',
            'email': email
        }
        
        return self._submit_transaction(payload)
    
    def query_accounts_by_type(self, account_type: str) -> Dict:
        """Query all accounts of a specific type."""
        payload = {
            'action': 'account_query',
            'query_type': 'by_account_type',
            'account_type': account_type
        }
        
        return self._submit_transaction(payload)
    
    def _submit_transaction(self, payload: Dict) -> Dict:
        """Submit a transaction to the blockchain."""
        # Create transaction
        payload["timestamp"] = self.serializer.get_current_timestamp()
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Generate addresses
        input_addresses = output_addresses = self._get_addresses()
        
        # Create transaction header
        txn_header = TransactionHeader(
            family_name='craftlore-account',
            family_version='1.0',
            inputs=input_addresses,
            outputs=output_addresses,
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
    
    def _get_addresses(self) -> list:
        """Get all possible addresses for account operations."""
        from utils.address_generator import AccountAddressGenerator
        
        address_gen = AccountAddressGenerator()
        namespace = address_gen.get_namespace()
        
        # Return the full namespace to allow any address within it
        return [namespace]
    
    def _wait_for_batch_commit(self, batch_id: str, timeout: int = 30) -> Dict:
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
    
    def create_new_client_key(self) -> str:
        """Create a new client with different key pair."""
        new_private_key = self.context.new_random_private_key()
        new_signer = self.crypto_factory.new_signer(new_private_key)
        new_public_key = new_signer.get_public_key().as_hex()
        
        # Create new client instance
        new_client = AccountTPClient(self.base_url)
        new_client.private_key = new_private_key
        new_client.signer = new_signer
        new_client.public_key = new_public_key
        
        return new_client


def main():
    """Demo script for Account TP."""
    print("🚀 CraftLore Account TP Client Demo")
    print("=" * 50)
    
    # Initialize client
    client = AccountTPClient()
    
    try:
        print("\n📋 Test 1: Create SuperAdmin Account (Bootstrap)")
        result = client.create_account(
            account_type='super_admin',
            email='admin@craftlore.com'
        )
        print(f"Result: {result}")
        
        # Store the admin public key for later use
        admin_key = client.public_key
        
        # print("\n📋 Test 2: Create Artisan Account")
        # artisan_client = client.create_new_client_key()
        # result = artisan_client.create_account(
        #     account_type='artisan',
        #     email='artisan@craftlore.com',
        #     specialization=['carpet_weaving', 'traditional_patterns'],
        #     skill_level='master_craftsman',
        #     years_experience=15
        # )
        # print(f"Result: {result}")
        
        # # Store artisan key
        # artisan_key = artisan_client.public_key
        
        # print("\n📋 Test 3: Authenticate Artisan Account")
        # result = client.authenticate_account(artisan_key, 'approve')
        # print(f"Result: {result}")
        
        # print("\n📋 Test 4: Create Buyer Account")
        # buyer_client = client.create_new_client_key()
        # result = buyer_client.create_account(
        #     account_type='buyer',
        #     email='buyer@craftlore.com',
        #     buyer_type='individual_collector',
        #     purchase_interests=['carpets', 'shawls']
        # )
        # print(f"Result: {result}")
        
        # print("\n📋 Test 5: Query Account by Public Key")
        # result = client.query_account_by_public_key(artisan_key)
        # print(f"Result: {result}")
        
        # print("\n📋 Test 6: Query Account by Email")
        # result = client.query_account_by_email('artisan@craftlore.com')
        # print(f"Result: {result}")
        
        # print("\n📋 Test 7: Query All Artisan Accounts")
        # result = client.query_accounts_by_type('artisan')
        # print(f"Result: {result}")
        
        # print("\n📋 Test 8: Update Artisan Account")
        # result = artisan_client.update_account(
        #     specialization=['carpet_weaving', 'traditional_patterns', 'contemporary_designs']
        # )
        # print(f"Result: {result}")
        
        # print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
