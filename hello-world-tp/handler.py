import hashlib
import json
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context 
from sawtooth_sdk.processor.exceptions import InvalidTransaction

def _make_hello_world_address(name):
    """Create a deterministic address for storing greetings"""
    return hashlib.sha512(
        ('hello_world' + name).encode('utf-8')
    ).hexdigest()[:70]

def _make_read_address(signer):
    """Create a deterministic address for storing read confirmations"""
    return hashlib.sha512(
        ('read_all_' + signer).encode('utf-8')
    ).hexdigest()[:70]

class HelloWorldTransactionHandler(TransactionHandler):
    family_name = 'hello_world'
    family_versions = ['1.0']
    namespaces = [_make_hello_world_address('')[:6]]

    def __init__(self):
        super().__init__()
        # Initialize any additional attributes or resources if needed

    def apply(self, transaction, context: Context):
        header = transaction.header
        signer = header.signer_public_key
        
        try:
            payload = json.loads(transaction.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise InvalidTransaction("Invalid payload format. Expected JSON.")
        
        action = payload.get('action')
        
        if action == 'write':
            name = payload.get('name', '').strip()
            if not name:
                raise InvalidTransaction("Name is required for write action")
            self._write_greeting(context, signer, name)
        elif action == 'read':
            self._read_greetings(context, signer)
        else:
            raise InvalidTransaction("Invalid action. Must be 'read' or 'write'")

    def _write_greeting(self, context: Context, signer, name):
        """Write a greeting to the blockchain"""
        greeting_data = {
            'message': f"Hello {name}",
            'author': signer,
            'name': name
        }
        
        address = _make_hello_world_address(name)
        
        context.set_state({
            address: json.dumps(greeting_data).encode('utf-8')
        })
        
        print(f"Stored greeting: Hello {name} by {signer[:8]}...")


    def _read_greetings(self, context: Context, signer):
        pass


