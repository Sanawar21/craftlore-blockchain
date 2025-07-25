from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context 
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from object import CraftloreObject
from abc import abstractmethod
import hashlib
import json

class CraftLoreTransactionHandler(TransactionHandler):

    @abstractmethod
    @property
    def prefix(self):
        """
        prefix should return the unique prefix for this transaction family.
        This is used to create deterministic addresses for transactions.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def make_address(self, identifier):
        """Create a deterministic address based on prefix and identifier."""
        return hashlib.sha512(
            (self.prefix + identifier).encode('utf-8')
        ).hexdigest()[:70]


class CraftLoreObjectTransactionHandler(CraftLoreTransactionHandler):
    """
    Base class for CraftLore transaction handlers that manage objects.
    Subclasses should implement the `prefix` property and the `apply` method.
    """

    def apply(self, transaction, context: Context):
        """
        Apply the transaction to the context. This method must be implemented by subclasses.
        """
        header = transaction.header
        signer = header.signer_public_key
        
        try:
            payload = json.loads(transaction.payload.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise InvalidTransaction("Invalid payload format. Expected JSON.")
        
        action = payload.get('action')
        object = payload.get('object')
        identifier = payload.get('identifier') # if it is a create transaction, this can be None

        # read object from the blockchain and match identifier
        if not identifier and action != 'create':
            raise InvalidTransaction("Identifier is required for the action.")
        try:
            blockchain_object = self._read_object(context, identifier)
            # if blockchain_object.identifier 

        except InvalidTransaction:
            if action != 'create':
                raise InvalidTransaction(f"Object with identifier {identifier} does not exist.")
            else:
                # If creating, we can proceed without reading the object
                object = CraftloreObject.new(**object)

        if action == 'create':
            self.create_type(identifier)
        elif action == 'read':
            self.read_type(identifier)
        elif action == 'update':
            if object.get('owner') != signer:
                raise InvalidTransaction("Only the owner can update the object.")
            self.update_type(identifier, object)
        elif action == 'delete':
            if object.get('owner') != signer:
                raise InvalidTransaction("Only the owner can delete the object.")
            self.delete_type(identifier)
        else:
            raise InvalidTransaction("Invalid action. Must be 'create', 'read', 'update', or 'delete'.")


    
    def update_history(self, context: Context, identifier, data):
        """Update the history of an object in the blockchain."""
        address = self.make_address("historyof"+self.prefix+identifier)
        history_data = {
            'identifier': identifier,
            'data': data,
            'timestamp': context.get_time()
        }
        
        context.set_state({
            address: json.dumps(history_data).encode('utf-8')
        })

    def _read_object(self, context: Context, identifier):
        """Read the state at the address for the given identifier."""
        address = self.make_address(identifier)
        state = context.get_state([address])
        
        if not state:
            raise InvalidTransaction(f"Object with identifier {identifier} does not exist.")
        
        return CraftloreObject.from_json(json.loads(state[0].data.decode('utf-8')))

    def create_type(self, identifier):
        """Create a new address for the given identifier."""
        return self.make_address(identifier)
    
    def read_type(self, identifier):
        """Read the state at the address for the given identifier."""
        address = self.make_address(identifier)
        return address

    def update_type(self, identifier, data):
        """Update the state at the address for the given identifier with new data.
        Only the owner can update the object."""
        address = self.make_address(identifier)
        return address, json.dumps(data).encode('utf-8')
    
    def delete_type(self, identifier):
        """Delete the state at the address for the given identifier.
        Only the owner can delete the object."""
        address = self.make_address(identifier)
        return address


        
class CraftLoreAuthenticatorTransactionHandler(CraftLoreTransactionHandler):
    """
    Base class for CraftLore transaction handlers that manage authentication.
    Subclasses should implement the `prefix` property and the `apply` method.
    """

    @abstractmethod
    def apply(self, transaction, context: Context):
        """
        Apply the authentication transaction to the context. This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
        