from .base import BaseSubHandler, InvalidTransaction, Context
import json

class GetValueSubHandler(BaseSubHandler):
    """Subhandler for setting a value in the account transaction processor."""

    def apply(self, transaction, context: Context, payload: dict):
        """Handle 'get' action - retrieve a value by key."""
        key = payload.get('key')
        
        if not key:
            raise InvalidTransaction("'get' action requires 'key'")
        
        # Generate address
        address = self.get_address(key)
        
        # Get the data
        entries = context.get_state([address])
        
        if entries:
            stored_data = json.loads(entries[0].data.decode('utf-8'))
            value = stored_data.get('value')
            print(f"📖 Retrieved {key} = {value}")
            return {'status': 'success', 'key': key, 'value': value}
        else:
            print(f"❌ Key '{key}' not found")
            raise InvalidTransaction(f"Key '{key}' not found")