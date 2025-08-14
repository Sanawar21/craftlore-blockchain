#!/usr/bin/env python3
"""
Base client for CraftLore Asset TP.
Handles common functionality like transaction creation, submission, and state reading.
"""

import hashlib
import base64
import json
import time
import requests
from typing import Dict, List, Optional, Any
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList


class AssetClient:
    """Base client for interacting with CraftLore Asset TP."""
    
    # Transaction family information
    FAMILY_NAME = 'craftlore-asset'
    FAMILY_VERSION = '1.0'
    NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]

    
    ACCOUNT_FAMILY_NAME = 'craftlore-account' 
    ACCOUNT_FAMILY_NAMESPACE = hashlib.sha512(FAMILY_NAME.encode()).hexdigest()[:6]
    
    # Asset type prefixes (must match address_generator.py)
    ASSET_TYPE_PREFIXES = {
        'raw_material': '01',
        'product': '02',
        'product_batch': '03',
        'work_order': '04',
        'warranty': '05'
    }
    
    # Index prefixes
    OWNER_INDEX_PREFIX = 'ff'
    TYPE_INDEX_PREFIX = 'fe'
    BATCH_INDEX_PREFIX = 'fd'
    
    # def __init__(self, base_url: str = "http://localhost:8008", private_key_hex: str = None):
    def __init__(self, base_url: str = "http://rest-api:8008", private_key_hex: str = None):
        """
        Initialize client.
        
        Args:
            base_url: Sawtooth REST API endpoint
            private_key_hex: Private key for signing transactions (generates one if None)
        """
        self.base_url = base_url.rstrip('/')
        # Initialize cryptographic context
        self.context = create_context('secp256k1')
        self.crypto_factory = CryptoFactory(self.context)
        
        if private_key_hex:
            self.private_key = Secp256k1PrivateKey.from_hex(private_key_hex)
        else:
            self.private_key = self.context.new_random_private_key()
        
        self.public_key = self.context.get_public_key(self.private_key).as_hex()
        self.signer = self.crypto_factory.new_signer(self.private_key)
        
        print(f"Client initialized with public key: {self.public_key}")
        print(f"Client private key: {self.private_key.as_hex()}")

    def _create_transaction(self, payload: Dict, inputs: List, outputs: List):
        """Create a signed transaction."""
        # Serialize payload
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        # Create transaction header
        txn_header = TransactionHeader(
            family_name=self.FAMILY_NAME,
            family_version=self.FAMILY_VERSION,
            inputs=inputs,
            outputs=outputs,
            signer_public_key=self.public_key,
            batcher_public_key=self.public_key,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest(),
            nonce=str(time.time())
        ).SerializeToString()
        
        # Sign transaction header
        signature = self.signer.sign(txn_header)
        
        # Create transaction
        transaction = Transaction(
            header=txn_header,
            header_signature=signature,
            payload=payload_bytes
        )
        
        return transaction
    
    def _create_batch(self, transactions: List):
        """Create a batch from transactions."""
        transaction_signatures = [txn.header_signature for txn in transactions]
        
        batch_header = BatchHeader(
            signer_public_key=self.public_key,
            transaction_ids=transaction_signatures
        ).SerializeToString()
        
        signature = self.signer.sign(batch_header)
        
        batch = Batch(
            header=batch_header,
            header_signature=signature,
            transactions=transactions
        )
        
        return batch
    
    def _submit_batch(self, batch, wait: int = 30) -> Dict:
        """Submit batch to Sawtooth network."""
        batch_list = BatchList(batches=[batch])
        
        # Submit batch
        response = requests.post(
            f"{self.base_url}/batches",
            data=batch_list.SerializeToString(),
            headers={'Content-Type': 'application/octet-stream'}
        )
        
        if response.status_code != 202:
            raise Exception(f"Failed to submit batch: {response.status_code} - {response.text}")
        
        # Get batch ID for status checking
        batch_id = batch.header_signature
        
        # Wait for batch to be committed
        if wait > 0:
            return self._wait_for_batch(batch_id, wait)
        
        return {"batch_id": batch_id, "status": "submitted"}
    
    def _wait_for_batch(self, batch_id: str, timeout: int = 30) -> Dict:
        """Wait for batch to be committed."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(f"{self.base_url}/batch_statuses?id={batch_id}")
            
            if response.status_code == 200:
                batch_status = response.json()
                if batch_status.get('data'):
                    status = batch_status['data'][0]['status']
                    if status == 'COMMITTED':
                        return {"batch_id": batch_id, "status": "committed"}
                    elif status in ['INVALID', 'UNKNOWN']:
                        return {"batch_id": batch_id, "status": status, "error": "Batch failed"}
            
            time.sleep(1)
        
        return {"batch_id": batch_id, "status": "timeout"}
    
    def _make_asset_address(self, asset_id: str, asset_type: str) -> str:
        """Generate address for an asset."""
        type_prefix = self.ASSET_TYPE_PREFIXES.get(asset_type, '00')
        asset_hash = hashlib.sha512(asset_id.encode()).hexdigest()
        return self.NAMESPACE + type_prefix + asset_hash[:62]
    
    def _make_owner_index_address(self, owner_public_key: str) -> str:
        """Generate address for owner index."""
        owner_hash = hashlib.sha512(owner_public_key.encode()).hexdigest()
        return self.NAMESPACE + self.OWNER_INDEX_PREFIX + owner_hash[:62]
    
    def _make_type_index_address(self, asset_type: str) -> str:
        """Generate address for asset type index."""
        type_hash = hashlib.sha512(asset_type.encode()).hexdigest()
        return self.NAMESPACE + self.TYPE_INDEX_PREFIX + type_hash[:62]
    
    def _make_batch_index_address(self, batch_id: str) -> str:
        """Generate address for batch index."""
        batch_hash = hashlib.sha512(batch_id.encode()).hexdigest()
        return self.NAMESPACE + self.BATCH_INDEX_PREFIX + batch_hash[:62]
    
    def get_state(self, address: str) -> Optional[Dict]:
        """Get state data from a specific address."""
        response = requests.get(f"{self.base_url}/state/{address}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return json.loads(base64.b64decode(data['data']).decode('utf-8'))
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"Failed to get state: {response.status_code} - {response.text}")
        
        return None
    
    def get_asset(self, asset_id: str, asset_type: str) -> Optional[Dict]:
        """Get asset by ID and type."""
        address = self._make_asset_address(asset_id, asset_type)
        return self.get_state(address)
    
    def get_assets_by_owner(self, owner_public_key: str) -> List[Dict]:
        """Get all assets owned by a public key."""
        address = self._make_owner_index_address(owner_public_key)
        index_data = self.get_state(address)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            # Try each asset type to find the asset
            for asset_type in self.ASSET_TYPE_PREFIXES.keys():
                asset = self.get_asset(asset_id, asset_type)
                if asset:
                    assets.append(asset)
                    break
        
        return assets
    
    def get_assets_by_type(self, asset_type: str) -> List[Dict]:
        """Get all assets of a specific type."""
        address = self._make_type_index_address(asset_type)
        index_data = self.get_state(address)
        
        if not index_data or 'assets' not in index_data:
            return []
        
        assets = []
        for asset_id in index_data['assets']:
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                assets.append(asset)
        
        return assets
    
    def submit_transaction(self, action: str, data: Dict, wait: int = 30) -> Dict:
        """Submit a transaction with the specified action and data."""
        # Prepare payload
        payload = {
            'action': action,
            **data
        }
        
        # Calculate addresses for inputs/outputs
        inputs = [self.ACCOUNT_FAMILY_NAMESPACE, self.NAMESPACE]
        outputs = [self.ACCOUNT_FAMILY_NAMESPACE, self.NAMESPACE]
        
        # Add asset address if asset_id and asset_type are provided
        # if 'asset_id' in data and 'asset_type' in data:
        #     asset_address = self._make_asset_address(data['asset_id'], data['asset_type'])
        #     inputs.append(asset_address)
        #     outputs.append(asset_address)
        
        # # Add owner indices
        # if 'owner' in data:
        #     owner_address = self._make_owner_index_address(data['owner'])
        #     inputs.append(owner_address)
        #     outputs.append(owner_address)
        
        # if 'new_owner' in data:
        #     new_owner_address = self._make_owner_index_address(data['new_owner'])
        #     inputs.append(new_owner_address)
        #     outputs.append(new_owner_address)
        
        # # Add type index
        # if 'asset_type' in data:
        #     type_address = self._make_type_index_address(data['asset_type'])
        #     inputs.append(type_address)
        #     outputs.append(type_address)
        
        # # Add batch index if creating products from batch
        # if 'batch_id' in data:
        #     batch_address = self._make_batch_index_address(data['batch_id'])
        #     inputs.append(batch_address)
        #     outputs.append(batch_address)
            
        #     # Also add the batch asset itself
        #     batch_asset_address = self._make_asset_address(data['batch_id'], 'product_batch')
        #     inputs.append(batch_asset_address)
        #     outputs.append(batch_asset_address)
        
        # # Add current owner's index for transfers
        # current_asset = None
        # if action in ['transfer_asset', 'lock_asset', 'unlock_asset', 'delete_asset', 'update_asset']:
        #     if 'asset_id' in data and 'asset_type' in data:
        #         current_asset = self.get_asset(data['asset_id'], data['asset_type'])
        #         if current_asset and 'owner' in current_asset:
        #             current_owner_address = self._make_owner_index_address(current_asset['owner'])
        #             inputs.append(current_owner_address)
        #             outputs.append(current_owner_address)
        
        # # Remove duplicates
        # inputs = list(set(inputs))
        # outputs = list(set(outputs))
        
        # Create and submit transaction
        transaction = self._create_transaction(payload, inputs, outputs)
        batch = self._create_batch([transaction])
        
        return self._submit_batch(batch, wait)
    
    def print_asset(self, asset: Dict, show_history: bool = False):
        """Pretty print asset information."""
        if not asset:
            print("Asset not found.")
            return
        
        print(f"\n{'='*60}")
        print(f"Asset: {asset.get('asset_id')} ({asset.get('asset_type', 'Unknown').replace('_', ' ').title()})")
        print(f"{'='*60}")
        print(f"Owner: {asset.get('owner', 'Unknown')}")
        print(f"Status: {asset.get('status', 'Unknown')}")
        print(f"Created: {asset.get('created_timestamp', asset.get('created_at', 'Unknown'))}")
        
        if 'name' in asset:
            print(f"Name: {asset['name']}")
        if 'description' in asset:
            print(f"Description: {asset['description']}")
        if 'batch_id' in asset:
            print(f"Batch ID: {asset['batch_id']}")
        if 'warranty_id' in asset:
            print(f"Warranty: {asset['warranty_id']}")
        if 'work_order_id' in asset:
            print(f"Work Order: {asset['work_order_id']}")
        
        # Show certifications
        if 'certifications' in asset and asset['certifications']:
            print(f"\nCertifications:")
            for cert in asset['certifications']:
                print(f"  • {cert.get('certification_type')} by {cert.get('certifying_authority')}")
                print(f"    Status: {cert.get('status')}, Issued: {cert.get('issue_date')}")
        
        # Show warranty info
        if any(key.startswith('warranty_') for key in asset.keys()):
            print(f"\nWarranty Information:")
            if 'warranty_provider' in asset:
                print(f"  Provider: {asset['warranty_provider']}")
            if 'warranty_type' in asset:
                print(f"  Type: {asset['warranty_type']}")
            if 'warranty_start_date' in asset:
                print(f"  Start Date: {asset['warranty_start_date']}")
            if 'warranty_end_date' in asset:
                print(f"  End Date: {asset['warranty_end_date']}")
        
        # Show sustainability metrics
        if 'sustainability_metrics' in asset:
            print(f"\nSustainability Metrics:")
            for metric, value in asset['sustainability_metrics'].items():
                print(f"  • {metric.replace('_', ' ').title()}: {value}")
        
        # Show history if requested
        if show_history and 'history' in asset and asset['history']:
            print(f"\nHistory ({len(asset['history'])} entries):")
            for i, entry in enumerate(asset['history'][-5:], 1):  # Show last 5 entries
                print(f"  {i}. {entry.get('action', 'Unknown')} at {entry.get('timestamp', 'Unknown')}")
                if 'actor' in entry:
                    print(f"     by {entry['actor']}")
                if 'details' in entry:
                    print(f"     {entry['details']}")
        
        print(f"{'='*60}\n")
