from .base import BaseSubHandler, InvalidTransaction, Context
import json

class SetValueSubHandler(BaseSubHandler):
    """Subhandler for setting a value in the account transaction processor."""

    def apply(self, transaction, context: Context, payload: dict):
        """Handle 'set' action - store a key-value pair."""
        key = payload.get('key')
        value = payload.get('value')

        if not key:
            raise InvalidTransaction("'set' action requires 'key'")
        if not value:
            raise InvalidTransaction("'set' action requires 'value'")
        
        # Generate address
        address = self.get_address(key)
        
        # Create data to store
        data = {
            'key': key,
            'value': value,
            'signer': transaction.header.signer_public_key,
            'action': 'set'
        }
        
        # Store the data
        context.set_state({
            address: json.dumps(data).encode('utf-8')
        })
        
        print(f"✅ Set {key} = {value}")
        return {'status': 'success', 'key': key, 'value': value}