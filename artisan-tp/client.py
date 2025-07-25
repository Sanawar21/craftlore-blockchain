#!/usr/bin/env python3

import json
import hashlib
import requests
import time
import base64
from datetime import datetime
from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

def _make_artisan_address(artisan_id):
    """Create a deterministic address for storing artisan profiles"""
    return hashlib.sha512(
        ('artisan' + artisan_id).encode('utf-8')
    ).hexdigest()[:70]

def _make_product_address(product_id):
    """Create a deterministic address for storing product information"""
    return hashlib.sha512(
        ('product' + product_id).encode('utf-8')
    ).hexdigest()[:70]

def _make_transaction_address(transaction_id):
    """Create a deterministic address for storing transaction records"""
    return hashlib.sha512(
        ('transaction' + transaction_id).encode('utf-8')
    ).hexdigest()[:70]

class ArtisanClient:
    def __init__(self, rest_api_url='http://rest-api:8008'):
        self.rest_api_url = rest_api_url
        self.context = create_context('secp256k1')
        self.private_key = self.context.new_random_private_key()
        self.signer = CryptoFactory(self.context).new_signer(self.private_key)
        
        print(f"🔑 Private Key: {self.private_key.as_hex()}")
        print(f"🔑 Public Key: {self.signer.get_public_key().as_hex()}")

    def _create_transaction(self, payload_data, inputs, outputs):
        """Create a transaction"""
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        txn_header = TransactionHeader(
            family_name='artisan',
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

    def _submit_batch(self, transactions):
        """Submit a batch of transactions"""
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

    def _check_batch_status(self, batch_id):
        """Check batch status"""
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

    def create_artisan(self, artisan_id, name, location, speciality):
        """Create an artisan profile"""
        print(f"\n🎨 Creating artisan: {name}")
        
        payload_data = {
            'action': 'create_artisan',
            'artisan_id': artisan_id,
            'name': name,
            'location': location,
            'speciality': speciality,
            'timestamp': datetime.now().isoformat()
        }
        
        address = _make_artisan_address(artisan_id)
        transaction = self._create_transaction(payload_data, [address], [address])
        
        return self._submit_batch([transaction])

    def create_product(self, product_id, artisan_id, name, description, price, quantity=1):
        """Create a product listing"""
        print(f"\n📦 Creating product: {name}")
        
        payload_data = {
            'action': 'create_product',
            'product_id': product_id,
            'artisan_id': artisan_id,
            'name': name,
            'description': description,
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.now().isoformat()
        }
        
        artisan_address = _make_artisan_address(artisan_id)
        product_address = _make_product_address(product_id)
        
        transaction = self._create_transaction(
            payload_data, 
            [artisan_address, product_address], 
            [product_address]
        )
        
        return self._submit_batch([transaction])

    def buy_product(self, transaction_id, product_id, buyer_info=None):
        """Purchase a product"""
        print(f"\n💰 Buying product: {product_id}")
        
        payload_data = {
            'action': 'buy_product',
            'transaction_id': transaction_id,
            'product_id': product_id,
            'buyer_info': buyer_info or {},
            'timestamp': datetime.now().isoformat()
        }
        
        product_address = _make_product_address(product_id)
        transaction_address = _make_transaction_address(transaction_id)
        
        transaction = self._create_transaction(
            payload_data,
            [product_address],
            [product_address, transaction_address]
        )
        
        return self._submit_batch([transaction])

    def get_state(self, address):
        """Get state data from an address"""
        try:
            response = requests.get(f'{self.rest_api_url}/state/{address}')
            if response.status_code == 200:
                state_data = response.json()
                decoded_data = json.loads(base64.b64decode(state_data['data']).decode('utf-8'))
                return decoded_data
            else:
                print(f"❌ State not found at address: {address}")
                return None
        except Exception as e:
            print(f"❌ Error retrieving state: {e}")
            return None

def demo():
    """Run a demonstration of the artisan marketplace"""
    print("🎨 === Artisan Marketplace Demo ===")
    
    client = ArtisanClient()
    
    # Create an artisan
    artisan_success = client.create_artisan(
        artisan_id="artisan001",
        name="Master Craftsperson",
        location="Kashmir, India",
        speciality="Handwoven Carpets"
    )
    
    if artisan_success:
        # Create a product
        product_success = client.create_product(
            product_id="product001",
            artisan_id="artisan001",
            name="Traditional Kashmiri Carpet",
            description="Handwoven carpet with intricate patterns",
            price=500.00,
            quantity=5
        )
        
        if product_success:
            # Buy the product
            client.buy_product(
                transaction_id="txn001",
                product_id="product001",
                buyer_info={"name": "John Doe", "email": "john@example.com"}
            )
            
            # Check final state
            print("\n📊 Final States:")
            artisan_data = client.get_state(_make_artisan_address("artisan001"))
            if artisan_data:
                print(f"👨‍🎨 Artisan: {artisan_data}")
            
            product_data = client.get_state(_make_product_address("product001"))
            if product_data:
                print(f"📦 Product: {product_data}")

if __name__ == '__main__':
    demo()
