#!/usr/bin/env python3
"""
CraftLore Client for testing blockchain transactions.
Demonstrates all transaction types supported by the CraftLore system.
"""

import json
import hashlib
import requests
import time
from datetime import datetime
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

from object import AuthenticationStatus, AccountType

class CraftLoreClient:
    """Client for interacting with the CraftLore blockchain."""
    
    def __init__(self, rest_api_url='http://rest-api:8008'):
        self.rest_api_url = rest_api_url
        self.context = create_context('secp256k1')
        self.private_key = self.context.new_random_private_key()
        self.signer = CryptoFactory(self.context).new_signer(self.private_key)
        
        # CraftLore namespace
        self.namespace = hashlib.sha512('craftlore'.encode('utf-8')).hexdigest()[:6]
        
        print(f"🔑 Client initialized")
        print(f"🔑 Public Key: {self.signer.get_public_key().as_hex()}")
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate blockchain address."""
        return hashlib.sha512(
            f"craftlore_{prefix}_{identifier}".encode('utf-8')
        ).hexdigest()[:70]
    
    def _create_transaction(self, payload_data: dict, inputs: list, outputs: list):
        """Create a transaction."""
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        txn_header = TransactionHeader(
            family_name='craftlore',
            family_version='1.0',
            inputs=inputs,
            outputs=outputs,
            signer_public_key=self.signer.get_public_key().as_hex(),
            batcher_public_key=self.signer.get_public_key().as_hex(),
            dependencies=[],
            payload_sha512=hashlib.sha512(payload_bytes).hexdigest()
        )
        
        txn_header_bytes = txn_header.SerializeToString()
        signature = self.signer.sign(txn_header_bytes)
        
        return Transaction(
            header=txn_header_bytes,
            header_signature=signature,
            payload=payload_bytes
        )
    
    def _submit_batch(self, transactions: list):
        """Submit a batch of transactions."""
        batch_header = BatchHeader(
            signer_public_key=self.signer.get_public_key().as_hex(),
            transaction_ids=[txn.header_signature for txn in transactions],
        )
        
        batch_header_bytes = batch_header.SerializeToString()
        batch_signature = self.signer.sign(batch_header_bytes)
        
        batch = Batch(
            header=batch_header_bytes,
            header_signature=batch_signature,
            transactions=transactions
        )
        
        batch_list = BatchList(batches=[batch])
        batch_list_bytes = batch_list.SerializeToString()
        
        try:
            response = requests.post(
                f'{self.rest_api_url}/batches',
                headers={'Content-Type': 'application/octet-stream'},
                data=batch_list_bytes,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            print("✅ Transaction submitted successfully!")
            
            batch_id = batch.header_signature
            print(f"📦 Batch ID: {batch_id}")
            
            # Wait and check status
            time.sleep(2)
            return self._check_batch_status(batch_id)
            
        except Exception as e:
            print(f"❌ Error submitting transaction: {e}")
            return False
    
    def _check_batch_status(self, batch_id: str):
        """Check batch status."""
        try:
            response = requests.get(f'{self.rest_api_url}/batch_statuses?id={batch_id}')
            response.raise_for_status()
            
            result = response.json()
            batch_status = result.get('data', [{}])[0].get('status', 'UNKNOWN')
            
            if batch_status == 'COMMITTED':
                print("✅ Transaction committed successfully!")
                return True
            else:
                print(f"❌ Transaction status: {batch_status}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return False
    
    # =============================================
    # ACCOUNT TRANSACTIONS
    # =============================================
    
    def create_account(self, account_type: AccountType, account_data: dict):
        """Create a new account."""
        print(f"\n👤 Creating {account_type.value} account...")
        
        payload_data = {
            'action': 'account_create',
            'account_type': account_type.value,
            'account_data': account_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Generate addresses
        account_id = account_data.get('account_id', 'generated_id')
        account_address = self._generate_address('account', account_id)
        
        transaction = self._create_transaction(
            payload_data,
            [account_address],
            [account_address]
        )
        
        return self._submit_batch([transaction])
    
    def authenticate_account(self, account_id: str, status: AuthenticationStatus, reason: str = ""):
        """Authenticate an account."""
        print(f"\n🔐 Authenticating account {account_id}...")
        
        payload_data = {
            'action': 'account_authenticate',
            'account_id': account_id,
            'status': status.value,
            'reason': reason,
            'block_number': int(time.time()),
            'timestamp': datetime.now().isoformat()
        }
        
        account_address = self._generate_address('account', account_id)
        
        transaction = self._create_transaction(
            payload_data,
            [account_address],
            [account_address]
        )
        
        return self._submit_batch([transaction])
    
    # =============================================
    # MATERIAL TRANSACTIONS
    # =============================================
    
    def record_material_harvest(self, material_data: dict):
        """Record raw material harvesting."""
        print(f"\n🌾 Recording material harvest...")
        
        payload_data = {
            'action': 'material_harvest',
            'material_data': material_data,
            'timestamp': datetime.now().isoformat()
        }
        
        material_id = material_data.get('material_id', 'generated_id')
        material_address = self._generate_address('material', material_id)
        
        transaction = self._create_transaction(
            payload_data,
            [material_address],
            [material_address]
        )
        
        return self._submit_batch([transaction])
    
    # =============================================
    # PRODUCT TRANSACTIONS
    # =============================================
    
    def create_product(self, product_data: dict):
        """Create a new handicraft product."""
        print(f"\n🎨 Creating product...")
        
        payload_data = {
            'action': 'product_create',
            'product_data': product_data,
            'timestamp': datetime.now().isoformat()
        }
        
        product_id = product_data.get('product_id', 'generated_id')
        product_address = self._generate_address('product', product_id)
        
        transaction = self._create_transaction(
            payload_data,
            [product_address],
            [product_address]
        )
        
        return self._submit_batch([transaction])
    
    def update_product_progress(self, product_id: str, progress_data: dict):
        """Update product production progress."""
        print(f"\n📈 Updating product progress...")
        
        payload_data = {
            'action': 'product_update_progress',
            'product_id': product_id,
            'progress_data': progress_data,
            'timestamp': datetime.now().isoformat()
        }
        
        product_address = self._generate_address('product', product_id)
        
        transaction = self._create_transaction(
            payload_data,
            [product_address],
            [product_address]
        )
        
        return self._submit_batch([transaction])
    
    # =============================================
    # ORDER TRANSACTIONS
    # =============================================
    
    def create_work_order(self, order_data: dict):
        """Create a work order."""
        print(f"\n📋 Creating work order...")
        
        payload_data = {
            'action': 'order_create',
            'order_data': order_data,
            'timestamp': datetime.now().isoformat()
        }
        
        order_id = order_data.get('order_id', 'generated_id')
        order_address = self._generate_address('order', order_id)
        
        transaction = self._create_transaction(
            payload_data,
            [order_address],
            [order_address]
        )
        
        return self._submit_batch([transaction])
    
    # =============================================
    # BUSINESS TRANSACTIONS
    # =============================================
    
    def record_purchase(self, transaction_data: dict):
        """Record a business transaction."""
        print(f"\n💰 Recording purchase transaction...")
        
        payload_data = {
            'action': 'transaction_purchase',
            'transaction_data': transaction_data,
            'timestamp': datetime.now().isoformat()
        }
        
        txn_id = transaction_data.get('transaction_id', 'generated_id')
        txn_address = self._generate_address('transaction', txn_id)
        
        transaction = self._create_transaction(
            payload_data,
            [txn_address],
            [txn_address]
        )
        
        return self._submit_batch([transaction])
    
    # =============================================
    # CERTIFICATE TRANSACTIONS
    # =============================================
    
    def issue_certificate(self, certificate_data: dict):
        """Issue a certificate."""
        print(f"\n📜 Issuing certificate...")
        
        payload_data = {
            'action': 'certificate_issue',
            'certificate_data': certificate_data,
            'timestamp': datetime.now().isoformat()
        }
        
        cert_id = certificate_data.get('certificate_id', 'generated_id')
        cert_address = self._generate_address('certificate', cert_id)
        
        transaction = self._create_transaction(
            payload_data,
            [cert_address],
            [cert_address]
        )
        
        return self._submit_batch([transaction])

def demo_craftlore_blockchain():
    """Demonstrate the complete CraftLore blockchain system."""
    
    print("🎨 === CraftLore Blockchain Demo ===\n")
    
    client = CraftLoreClient()
    
    # 1. Create accounts
    print("1. Creating accounts...")
    
    # Create Super Admin
    client.create_account(AccountType.SUPER_ADMIN, {
        'account_id': 'super_admin_001',
        'email': 'admin@craftlore.com'
    })
    
    # Create Artisan Admin
    client.create_account(AccountType.ARTISAN_ADMIN, {
        'account_id': 'artisan_admin_001',
        'email': 'artisan.admin@craftlore.com',
        'region': 'Kashmir'
    })
    
    # Create Artisan
    client.create_account(AccountType.ARTISAN, {
        'account_id': 'artisan_001',
        'artisan_name': 'Master Weaver Ali',
        'specialization': 'Carpet Weaving',
        'years_experience': 25,
        'location': 'Srinagar, Kashmir'
    })
    
    # Create Supplier
    client.create_account(AccountType.SUPPLIER, {
        'account_id': 'supplier_001',
        'business_name': 'Kashmir Wool Suppliers',
        'material_types': ['wool', 'silk']
    })
    
    time.sleep(3)  # Wait for transactions to process
    
    # 2. Authenticate accounts
    print("\n2. Authenticating accounts...")
    
    client.authenticate_account('artisan_admin_001', AuthenticationStatus.APPROVED, 
                               "Verified credentials and authority")
    client.authenticate_account('artisan_001', AuthenticationStatus.APPROVED, 
                               "Verified skills and experience")
    client.authenticate_account('supplier_001', AuthenticationStatus.APPROVED, 
                               "Verified business license")
    
    time.sleep(3)
    
    # 3. Record material harvest
    print("\n3. Recording material harvest...")
    
    client.record_material_harvest({
        'material_id': 'wool_batch_001',
        'material_type': 'wool',
        'harvest_date': '2025-01-01',
        'quantity': 100,
        'source_location': 'Kashmir Valley, 34.0837°N, 74.7973°E',
        'certifications': ['organic', 'sustainable']
    })
    
    time.sleep(3)
    
    # 4. Create product
    print("\n4. Creating handicraft product...")
    
    client.create_product({
        'product_id': 'carpet_001',
        'product_name': 'Traditional Kashmiri Carpet',
        'product_type': 'carpet',
        'artisan_id': 'artisan_001',
        'materials_used': ['wool_batch_001'],
        'estimated_completion': '2025-03-01',
        'price': 500.0
    })
    
    time.sleep(3)
    
    # 5. Create work order
    print("\n5. Creating work order...")
    
    client.create_work_order({
        'order_id': 'order_001',
        'artisan_id': 'artisan_001',
        'product_type': 'carpet',
        'assigned_date': datetime.now().isoformat(),
        'expected_completion': '2025-03-01',
        'payment_terms': {'amount': 300.0, 'currency': 'USD'}
    })
    
    time.sleep(3)
    
    # 6. Update product progress
    print("\n6. Updating product progress...")
    
    client.update_product_progress('carpet_001', {
        'stage': 'weaving',
        'progress_percentage': 50,
        'time_spent_hours': 120,
        'photos': ['progress_photo_1.jpg'],
        'notes': 'Pattern foundation completed'
    })
    
    time.sleep(3)
    
    # 7. Issue certificate
    print("\n7. Issuing GI certificate...")
    
    client.issue_certificate({
        'certificate_id': 'gi_cert_001',
        'certificate_type': 'GI',
        'holder_id': 'carpet_001',
        'issuing_authority': 'Kashmir Craft Council',
        'issue_date': datetime.now().isoformat(),
        'certificate_data': {
            'geographic_origin': 'Kashmir',
            'traditional_methods': True,
            'authenticity_verified': True
        }
    })
    
    time.sleep(3)
    
    # 8. Record purchase transaction
    print("\n8. Recording purchase transaction...")
    
    client.record_purchase({
        'transaction_id': 'purchase_001',
        'buyer_id': 'buyer_001',
        'seller_id': 'artisan_001',
        'product_id': 'carpet_001',
        'amount': 500.0,
        'payment_method': 'crypto',
        'royalty_info': {
            'artisan_percentage': 5.0,
            'artisan_address': 'artisan_wallet_001'
        }
    })
    
    print("\n🎉 CraftLore blockchain demo completed!")
    print("All transactions demonstrate the complete supply chain from material sourcing to final sale.")

if __name__ == '__main__':
    demo_craftlore_blockchain()
