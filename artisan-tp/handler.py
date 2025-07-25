import hashlib
import json
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context 
from sawtooth_sdk.processor.exceptions import InvalidTransaction

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

class ArtisanTransactionHandler(TransactionHandler):
    family_name = 'artisan'
    family_versions = ['1.0']
    namespaces = [
        _make_artisan_address('')[:6],
        _make_product_address('')[:6],
        _make_transaction_address('')[:6]
    ]
    

    def __init__(self):
        super().__init__()
        print("🎨 Artisan Transaction Handler initialized")

    def apply(self, transaction, context: Context):
        print("🔄 Processing artisan transaction...")
        header = transaction.header
        signer = header.signer_public_key
        
        try:
            payload = json.loads(transaction.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise InvalidTransaction("Invalid payload format. Expected JSON.")
        
        action = payload.get('action')
        
        if action == 'create_artisan':
            self._create_artisan(context, signer, payload)
        elif action == 'create_product':
            self._create_product(context, signer, payload)
        elif action == 'buy_product':
            self._buy_product(context, signer, payload)
        elif action == 'get_artisan':
            self._get_artisan(context, payload)
        elif action == 'get_product':
            self._get_product(context, payload)
        else:
            raise InvalidTransaction(f"Invalid action: {action}")

    def _create_artisan(self, context: Context, signer, payload):
        """Create an artisan profile"""
        artisan_id = payload.get('artisan_id')
        name = payload.get('name')
        location = payload.get('location')
        speciality = payload.get('speciality')
        
        if not all([artisan_id, name, location, speciality]):
            raise InvalidTransaction("Missing required fields: artisan_id, name, location, speciality")
        
        artisan_data = {
            'artisan_id': artisan_id,
            'name': name,
            'location': location,
            'speciality': speciality,
            'owner': signer,
            'created_at': payload.get('timestamp', ''),
            'products': []
        }
        
        address = _make_artisan_address(artisan_id)
        
        context.set_state({
            address: json.dumps(artisan_data).encode('utf-8')
        })
        
        print(f"✅ Created artisan: {name} ({artisan_id}) by {signer[:8]}...")

    def _create_product(self, context: Context, signer, payload):
        """Create a product listing"""
        product_id = payload.get('product_id')
        artisan_id = payload.get('artisan_id')
        name = payload.get('name')
        description = payload.get('description')
        price = payload.get('price')
        quantity = payload.get('quantity', 1)
        
        if not all([product_id, artisan_id, name, description, price]):
            raise InvalidTransaction("Missing required fields: product_id, artisan_id, name, description, price")
        
        # Verify artisan exists and signer owns it
        artisan_address = _make_artisan_address(artisan_id)
        artisan_entries = context.get_state([artisan_address])
        
        if not artisan_entries:
            raise InvalidTransaction(f"Artisan {artisan_id} not found")
        
        artisan_data = json.loads(artisan_entries[0].data.decode('utf-8'))
        if artisan_data.get('owner') != signer:
            raise InvalidTransaction("Only the artisan owner can create products")
        
        product_data = {
            'product_id': product_id,
            'artisan_id': artisan_id,
            'name': name,
            'description': description,
            'price': price,
            'quantity': quantity,
            'created_at': payload.get('timestamp', ''),
            'status': 'available'
        }
        
        address = _make_product_address(product_id)
        
        context.set_state({
            address: json.dumps(product_data).encode('utf-8')
        })
        
        print(f"✅ Created product: {name} ({product_id}) by artisan {artisan_id}")

    def _buy_product(self, context: Context, signer, payload):
        """Purchase a product"""
        transaction_id = payload.get('transaction_id')
        product_id = payload.get('product_id')
        buyer_info = payload.get('buyer_info', {})
        
        if not all([transaction_id, product_id]):
            raise InvalidTransaction("Missing required fields: transaction_id, product_id")
        
        # Get product information
        product_address = _make_product_address(product_id)
        product_entries = context.get_state([product_address])
        
        if not product_entries:
            raise InvalidTransaction(f"Product {product_id} not found")
        
        product_data = json.loads(product_entries[0].data.decode('utf-8'))
        
        if product_data.get('status') != 'available':
            raise InvalidTransaction("Product is not available")
        
        if product_data.get('quantity', 0) <= 0:
            raise InvalidTransaction("Product is out of stock")
        
        # Create transaction record
        transaction_data = {
            'transaction_id': transaction_id,
            'product_id': product_id,
            'artisan_id': product_data.get('artisan_id'),
            'buyer': signer,
            'buyer_info': buyer_info,
            'price': product_data.get('price'),
            'timestamp': payload.get('timestamp', ''),
            'status': 'completed'
        }
        
        # Update product quantity
        product_data['quantity'] = product_data['quantity'] - 1
        if product_data['quantity'] <= 0:
            product_data['status'] = 'sold_out'
        
        transaction_address = _make_transaction_address(transaction_id)
        
        context.set_state({
            transaction_address: json.dumps(transaction_data).encode('utf-8'),
            product_address: json.dumps(product_data).encode('utf-8')
        })
        
        print(f"✅ Purchase completed: {transaction_id} for product {product_id}")

    def _get_artisan(self, context: Context, payload):
        """Retrieve artisan information"""
        artisan_id = payload.get('artisan_id')
        if not artisan_id:
            raise InvalidTransaction("Missing artisan_id")
        
        address = _make_artisan_address(artisan_id)
        entries = context.get_state([address])
        
        if not entries:
            raise InvalidTransaction(f"Artisan {artisan_id} not found")
        
        artisan_data = json.loads(entries[0].data.decode('utf-8'))
        print(f"📋 Retrieved artisan: {artisan_data.get('name')}")

    def _get_product(self, context: Context, payload):
        """Retrieve product information"""
        product_id = payload.get('product_id')
        if not product_id:
            raise InvalidTransaction("Missing product_id")
        
        address = _make_product_address(product_id)
        entries = context.get_state([address])
        
        if not entries:
            raise InvalidTransaction(f"Product {product_id} not found")
        
        product_data = json.loads(entries[0].data.decode('utf-8'))
        print(f"📦 Retrieved product: {product_data.get('name')}")
