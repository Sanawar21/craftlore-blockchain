#!/usr/bin/env python3
"""
CraftLore Combined TP Client
Client for interacting with the unified CraftLore Transaction Processor.
"""

import json
import time
import hashlib
import requests
from utils.serialization import SerializationHelper
from utils.address_generator import CraftLoreAddressGenerator
from typing import Dict, Optional, List
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey


class CraftLoreClient:
    """Client for CraftLore Combined Transaction Processor."""
    
    def __init__(self, base_url: str = 'http://rest-api:8008', private_key: Optional[str] = None):
        self.base_url = base_url
        self.context = create_context('secp256k1')
        self.crypto_factory = CryptoFactory(self.context)
        self.serializer = SerializationHelper()
        self.address_generator = CraftLoreAddressGenerator()
        
        # Generate or use provided private key
        if private_key:
            self.private_key = Secp256k1PrivateKey.from_hex(private_key)
        else:
            self.private_key = self.context.new_random_private_key()
            
        self.signer = self.crypto_factory.new_signer(self.private_key)
        self.public_key = self.signer.get_public_key().as_hex()
        
        print(f"Client initialized with public key: {self.public_key}")
        if not private_key:
            print(f"Client private key: {self.private_key.as_hex()} (keep it secret!)")
    
    # ===========================
    # ACCOUNT OPERATIONS
    # ===========================
    
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
    
    def update_account(self, target_public_key: str = None, **updates) -> Dict:
        """Update account information."""
        payload = {
            'action': 'account_update',
            'timestamp': self.serializer.get_current_timestamp(),
            **updates
        }
        
        if target_public_key:
            payload['target_public_key'] = target_public_key
        
        return self._submit_transaction(payload)
    
    def deactivate_account(self, target_public_key: str) -> Dict:
        """Deactivate an account."""
        payload = {
            'action': 'account_deactivate',
            'target_public_key': target_public_key,
            'timestamp': self.serializer.get_current_timestamp()
        }
        
        return self._submit_transaction(payload)
    
    # ===========================
    # ASSET OPERATIONS
    # ===========================
    
    def create_asset(self, asset_type: str, asset_id: str, **asset_data) -> Dict:
        """Create a new asset."""
        payload = {
            'action': 'create_asset',
            'asset_type': asset_type,
            'asset_id': asset_id,
            'timestamp': self.serializer.get_current_timestamp(),
            **asset_data
        }
        
        return self._submit_transaction(payload)
    
    def create_raw_material(self, material_id: str, material_type: str, supplier_id: str, 
                          quantity: float, source_location: str, **kwargs) -> Dict:
        """Create a raw material asset."""
        return self.create_asset(
            asset_type='raw_material',
            asset_id=material_id,
            material_type=material_type,
            supplier_id=supplier_id,
            quantity=quantity,
            source_location=source_location,
            **kwargs
        )
    
    def create_work_order(self, work_order_id: str, buyer_id: str, product_batch_id: str,
                         assignee_id: str, description: str, order_quantity: int = 0, **kwargs) -> Dict:
        """Create a work order with specified quantity."""
        return self.create_asset(
            asset_type='work_order',
            asset_id=work_order_id,
            buyer_id=buyer_id,
            product_batch_id=product_batch_id,
            assignee_id=assignee_id,
            description=description,
            order_quantity=order_quantity,
            **kwargs
        )
    
    def create_product_batch(self, batch_id: str, batch_type: str, order_quantity: int,
                           assigned_artisan: str = None, **kwargs) -> Dict:
        """Create a product batch. Only artisan or workshop accounts can create product batches directly."""
        return self.create_asset(
            asset_type='product_batch',
            asset_id=batch_id,
            batch_type=batch_type,
            order_quantity=order_quantity,
            assigned_artisan=assigned_artisan,
            **kwargs
        )
    
    def transfer_asset(self, asset_id: str, asset_type: str, new_owner_public_key: str, **kwargs) -> Dict:
        """Transfer an asset to a new owner."""
        payload = {
            'action': 'transfer_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'new_owner_public_key': new_owner_public_key,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def accept_asset(self, asset_id: str, asset_type: str, **kwargs) -> Dict:
        """Accept a transferred asset."""
        payload = {
            'action': 'accept_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def sub_assign_work_order(self, work_order_id: str, assignee_ids: List[str], 
                             assignment_details: Dict = None, **kwargs) -> Dict:
        """Sub-assign a work order to individual artisans or workshops."""
        payload = {
            'action': 'sub_assign_work_order',
            'work_order_id': work_order_id,
            'assignee_ids': assignee_ids,
            'assignment_details': assignment_details or {},
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def accept_work_order(self, work_order_id: str, **kwargs) -> Dict:
        """Accept a work order (workshop accepting buyer's order)."""
        payload = {
            'action': 'accept_asset',
            'asset_id': work_order_id,
            'asset_type': 'work_order',
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def lock_asset(self, asset_id: str, asset_type: str, **kwargs) -> Dict:
        """Lock an asset to prevent modifications."""
        payload = {
            'action': 'lock_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def unlock_asset(self, asset_id: str, asset_type: str, **kwargs) -> Dict:
        """Unlock an asset to allow modifications."""
        payload = {
            'action': 'unlock_asset',
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def use_raw_material_in_batch(self, raw_material_id: str, batch_id: str, **kwargs) -> Dict:
        """Use a raw material in a product batch."""
        payload = {
            'action': 'use_raw_material_in_batch',
            'raw_material_id': raw_material_id,
            'batch_id': batch_id,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def complete_batch_production(self, batch_id: str, production_date: str = None, 
                                 artisans_involved: List[str] = None, quality_notes: str = '', **kwargs) -> Dict:
        """Complete batch production - mark batch as completed and update work order if linked."""
        payload = {
            'action': 'complete_batch_production',
            'batch_id': batch_id,
            'production_date': production_date or self.serializer.get_current_timestamp(),
            'artisans_involved': artisans_involved or [],
            'quality_notes': quality_notes,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    def register_warranty(self, product_id: str, warranty_period_months: int, **kwargs) -> Dict:
        """Register warranty for a product."""
        payload = {
            'action': 'register_warranty',
            'product_id': product_id,
            'warranty_period_months': warranty_period_months,
            'timestamp': self.serializer.get_current_timestamp(),
            **kwargs
        }
        
        return self._submit_transaction(payload)
    
    # ===========================
    # TRANSACTION HANDLING
    # ===========================
    
    def _submit_transaction(self, payload: Dict) -> Dict:
        """Submit a transaction to the blockchain."""
        try:
            # Create transaction
            transaction = self._create_transaction(payload)
            
            # Create batch
            batch = self._create_batch([transaction])
            
            # Submit batch
            batch_list = BatchList(batches=[batch])
            response = requests.post(
                f'{self.base_url}/batches',
                data=batch_list.SerializeToString(),
                headers={'Content-Type': 'application/octet-stream'}
            )
            
            if response.status_code != 202:
                return {
                    'status': 'error',
                    'message': f'Failed to submit transaction: {response.text}'
                }
            
            # Wait for result
            batch_id = batch.header_signature
            return self._wait_for_batch_completion(batch_id)
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Transaction submission failed: {str(e)}'
            }
    
    def _create_transaction(self, payload: Dict):
        """Create a transaction from payload."""
        # Serialize payload
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        # Use namespace prefix for inputs/outputs (simplified addressing)
        namespace = self.address_generator.get_namespace()
        
        # Create transaction header
        header = TransactionHeader(
            family_name='craftlore',
            family_version='1.0',
            inputs=[namespace],  # Use namespace prefix
            outputs=[namespace],  # Use namespace prefix
            signer_public_key=self.public_key,
            batcher_public_key=self.public_key,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
            nonce=str(time.time())
        )
        
        # Sign header
        header_bytes = header.SerializeToString()
        signature = self.signer.sign(header_bytes)
        
        # Create transaction
        return Transaction(
            header=header_bytes,
            header_signature=signature,
            payload=payload_bytes
        )
    
    def _create_batch(self, transactions: List):
        """Create a batch from transactions."""
        # Create batch header
        header = BatchHeader(
            signer_public_key=self.public_key,
            transaction_ids=[txn.header_signature for txn in transactions]
        )
        
        # Sign header
        header_bytes = header.SerializeToString()
        signature = self.signer.sign(header_bytes)
        
        # Create batch
        return Batch(
            header=header_bytes,
            header_signature=signature,
            transactions=transactions
        )
    
    def _wait_for_batch_completion(self, batch_id: str, timeout: int = 30) -> Dict:
        """Wait for batch to be committed and return status."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f'{self.base_url}/batch_statuses?id={batch_id}')
                
                if response.status_code == 200:
                    batch_status = response.json()
                    if batch_status['data']:
                        status = batch_status['data'][0]['status']
                        
                        if status == 'COMMITTED':
                            return {'status': 'success', 'batch_id': batch_id}
                        elif status in ['INVALID', 'UNKNOWN']:
                            return {
                                'status': 'error',
                                'message': f'Batch {status.lower()}',
                                'batch_id': batch_id
                            }
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error checking batch status: {e}")
                time.sleep(1)
        
        return {
            'status': 'timeout',
            'message': 'Transaction timed out',
            'batch_id': batch_id
        }
    
    # ===========================
    # UTILITY METHODS
    # ===========================
    
    def get_state(self, address: str) -> Optional[Dict]:
        """Get state data from a specific address."""
        try:
            response = requests.get(f'{self.base_url}/state/{address}')
            if response.status_code == 200:
                state_data = response.json()
                if state_data.get('data'):
                    # Decode base64 data
                    import base64
                    raw_data = base64.b64decode(state_data['data'])
                    return self.serializer.from_bytes(raw_data)
            return None
        except Exception as e:
            print(f"Error getting state: {e}")
            return None
    
    def get_account_address(self, public_key: str) -> str:
        """Get blockchain address for an account."""
        return self.address_generator.generate_account_address(public_key)
    
    def get_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Get blockchain address for an asset."""
        return self.address_generator.generate_asset_address(asset_id, asset_type)
    
    def list_all_state(self) -> List[Dict]:
        """List all state entries in the namespace."""
        try:
            namespace = self.address_generator.get_namespace()
            response = requests.get(f'{self.base_url}/state?address={namespace}')
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
        except Exception as e:
            print(f"Error listing state: {e}")
            return []


# Convenience function for quick client creation
def create_client(base_url: str = 'http://localhost:8008', private_key: str = None) -> CraftLoreClient:
    """Create a CraftLore client instance."""
    return CraftLoreClient(base_url, private_key)
