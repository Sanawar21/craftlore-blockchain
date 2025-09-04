#!/usr/bin/env python3
"""
CraftLore Combined TP Client
Client for interacting with the CraftLore Combined Transaction Processor.
"""

import json
import time
import hashlib
import requests
from typing import Dict, Optional
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from utils.serialization import SerializationHelper
from models.enums import AccountType, AssetType, EventType

class CraftLoreClient:
    """Client for CraftLore Combined Transaction Processor."""
    
    def __init__(self, base_url: str = 'http://rest-api:8008'):
        self.base_url = base_url
        self.context = create_context('secp256k1')
        self.crypto_factory = CryptoFactory(self.context)
        self.serializer = SerializationHelper()
        
        # Generate a private key for this client session
        self.private_key = self.context.new_random_private_key()
        self.signer = self.crypto_factory.new_signer(self.private_key)
        self.public_key = self.signer.get_public_key().as_hex()
        
        # Family information
        self.family_name = 'craftlore'
        self.family_version = '1.0'
        self.namespace = hashlib.sha512(self.family_name.encode()).hexdigest()[:6]
        
        print(f"Client initialized with public key: {self.public_key}")
        print(f"Client private key: {self.private_key.as_hex()} (keep it secret!)")

    # =============================================
    # ACCOUNT OPERATIONS
    # =============================================

    def create_account(self, account_type: AccountType, email: str, **kwargs) -> Dict:
        """Create a new account."""
        payload = {
            'event': EventType.ACCOUNT_CREATED.value,
            'timestamp': self.serializer.get_current_timestamp(),
            "fields": {
                'account_type': account_type.value,
                'email': email,
                **kwargs
            }
        }
        
        return self._submit_transaction(payload)
    
    def _submit_transaction(self, payload: Dict) -> Dict:
        """Submit a transaction to the blockchain."""
        try:
            # Create transaction
            transaction = self._create_transaction(payload)
            
            # Create batch
            batch = self._create_batch(transaction)
            
            # Submit batch
            response = self._submit_batch(batch)
            
            if response.get('success'):
                print(f"✅ Transaction submitted successfully: {response.get('link')}")
                return {
                    'status': 'success',
                    'transaction_id': transaction.header_signature,
                    'link': response.get('link')
                }
            else:
                print(f"❌ Transaction failed: {response}")
                return {
                    'status': 'failed',
                    'error': response
                }
                
        except Exception as e:
            print(f"❌ Error submitting transaction: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_transaction(self, payload: Dict):
        """Create a transaction from payload."""
        # Serialize payload
        payload_bytes = json.dumps(payload).encode('utf-8')
        
        # Create transaction header
        txn_header = TransactionHeader(
            family_name=self.family_name,
            family_version=self.family_version,
            inputs=[self.namespace],  # Use entire namespace for combined TP
            outputs=[self.namespace],
            signer_public_key=self.public_key,
            batcher_public_key=self.public_key,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
            nonce=str(time.time())
        )
        
        # Sign header
        signature = self.signer.sign(txn_header.SerializeToString())
        
        # Create transaction
        transaction = Transaction(
            header=txn_header.SerializeToString(),
            header_signature=signature,
            payload=payload_bytes
        )
        
        return transaction
    
    def _create_batch(self, transaction):
        """Create a batch containing the transaction."""
        # Create batch header
        batch_header = BatchHeader(
            signer_public_key=self.public_key,
            transaction_ids=[transaction.header_signature]
        )
        
        # Sign batch header
        signature = self.signer.sign(batch_header.SerializeToString())
        
        # Create batch
        batch = Batch(
            header=batch_header.SerializeToString(),
            header_signature=signature,
            transactions=[transaction]
        )
        
        return batch
    
    def _submit_batch(self, batch) -> Dict:
        """Submit batch to the REST API."""
        batch_list = BatchList(batches=[batch])
        
        response = requests.post(
            f'{self.base_url}/batches',
            headers={'Content-Type': 'application/octet-stream'},
            data=batch_list.SerializeToString()
        )
        
        if response.status_code == 202:
            response_data = response.json()
            return {
                'success': True,
                'link': response_data.get('link')
            }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'response': response.text
            }


def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    print("\n--- ACCOUNT OPERATIONS ---")
    print("1. Create Account")
        

    account_type = AccountType.SUPPLIER
    email = "s.com"
    result = client.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    time.sleep(1)
            


if __name__ == "__main__":
    main()
