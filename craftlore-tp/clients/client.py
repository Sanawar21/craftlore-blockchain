#!/usr/bin/env python3
"""
CraftLore Combined TP Client
Client for interacting with the CraftLore Combined Transaction Processor.
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
    
    def create_account(self, account_type: str, email: str, **kwargs) -> Dict:
        """Create a new account."""
        payload = {
            'action': 'account_create',
            'account_type': account_type,
            'email': email,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def authenticate_account(self, target_public_key: str, auth_decision: str) -> Dict:
        """Authenticate an account (approve/reject)."""
        payload = {
            'action': 'account_authenticate',
            'target_public_key': target_public_key,
            'auth_decision': auth_decision,
            'timestamp': self.serializer.get_current_timestamp()
        }
        
        return self._submit_transaction(payload)
    
    def query_account(self, query_type: str = 'by_public_key', **kwargs) -> Dict:
        """Query account information."""
        payload = {
            'action': 'account_query',
            'query_type': query_type,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)

    # =============================================
    # ASSET OPERATIONS
    # =============================================
    
    def create_asset(self, asset_type: str, asset_id: str, **kwargs) -> Dict:
        """Create a new asset."""
        payload = {
            'action': 'create_asset',
            'asset_type': asset_type,
            'asset_id': asset_id,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def transfer_asset(self, asset_id: str, asset_type: str, new_owner: str) -> Dict:
        """Transfer asset to new owner."""
        payload = {
            'action': 'transfer_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'new_owner': new_owner,
            'timestamp': self.serializer.get_current_timestamp()
        }
        
        return self._submit_transaction(payload)
    
    def lock_asset(self, asset_id: str, asset_type: str) -> Dict:
        """Lock an asset."""
        payload = {
            'action': 'lock_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': self.serializer.get_current_timestamp()
        }
        
        return self._submit_transaction(payload)
    
    def accept_asset(self, asset_id: str, asset_type: str) -> Dict:
        """Accept an asset (for work orders)."""
        payload = {
            'action': 'accept_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': self.serializer.get_current_timestamp()
        }
        
        return self._submit_transaction(payload)

    # =============================================
    # TRANSACTION HANDLING
    # =============================================
    
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
    
    while True:
        print("\n--- ACCOUNT OPERATIONS ---")
        print("1. Create Account")
        print("2. Authenticate Account")
        print("3. Query Account")
        
        print("\n--- ASSET OPERATIONS ---")
        print("4. Create Asset")
        print("5. Transfer Asset")
        print("6. Lock Asset")
        print("7. Accept Asset")
        
        print("\n--- GENERAL ---")
        print("8. Show My Public Key")
        print("9. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        try:
            if choice == '1':
                print("Available account types: buyer, seller, artisan, workshop, distributor, wholesaler, retailer, verifier, admin, super_admin, supplier")
                account_type = input("Enter account type: ").strip()
                email = input("Enter email: ").strip()
                result = client.create_account(account_type, email)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '2':
                target_key = input("Enter target public key: ").strip()
                decision = input("Enter decision (approve/reject): ").strip()
                result = client.authenticate_account(target_key, decision)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '3':
                query_type = input("Enter query type (by_public_key/by_email): ").strip()
                if query_type == 'by_public_key':
                    public_key = input("Enter public key (or press Enter for your own): ").strip()
                    if not public_key:
                        public_key = client.public_key
                    result = client.query_account(query_type, public_key=public_key)
                elif query_type == 'by_email':
                    email = input("Enter email: ").strip()
                    result = client.query_account(query_type, email=email)
                else:
                    print("Invalid query type")
                    continue
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '4':
                print("Available asset types: raw_material, product, product_batch, work_order, warranty")
                asset_type = input("Enter asset type: ").strip()
                asset_id = input("Enter asset ID: ").strip()
                
                # Collect additional fields based on asset type
                kwargs = {}
                if asset_type == 'raw_material':
                    kwargs['material_type'] = input("Enter material type: ").strip()
                    kwargs['quantity'] = input("Enter quantity: ").strip()
                    kwargs['source_location'] = input("Enter source location: ").strip()
                elif asset_type == 'work_order':
                    kwargs['assignee_id'] = input("Enter assignee public key: ").strip()
                    kwargs['work_type'] = input("Enter work type: ").strip()
                
                result = client.create_asset(asset_type, asset_id, **kwargs)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '5':
                asset_id = input("Enter asset ID: ").strip()
                asset_type = input("Enter asset type: ").strip()
                new_owner = input("Enter new owner public key: ").strip()
                result = client.transfer_asset(asset_id, asset_type, new_owner)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '6':
                asset_id = input("Enter asset ID: ").strip()
                asset_type = input("Enter asset type: ").strip()
                result = client.lock_asset(asset_id, asset_type)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '7':
                asset_id = input("Enter asset ID: ").strip()
                asset_type = input("Enter asset type: ").strip()
                result = client.accept_asset(asset_id, asset_type)
                print(f"Result: {json.dumps(result, indent=2)}")
            
            elif choice == '8':
                print(f"Your public key: {client.public_key}")
                print(f"Your private key: {client.private_key.as_hex()}")
            
            elif choice == '9':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
