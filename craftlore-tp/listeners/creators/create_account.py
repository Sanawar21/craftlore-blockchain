from typing import Any


from .. import BaseListener, EventType, EventContext, InvalidTransaction
from models.enums import AccountType
from models.classes.accounts import (SupplierAccount,)


class AccountCreationHandler(BaseListener):
    def __init__(self):
        super().__init__([EventType.ACCOUNT_CREATED], priorities=[1000]) # run before every other listener

    def on_event(self, event: EventContext):
        # Handle account creation event
        transaction = event.transaction
        context = event.context
        signature = event.signature
        payload = event.payload
        signer_public_key = event.signer_public_key

        fields: dict[str, Any] = payload.get("fields")
        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")

        fields = fields.copy() 

        fields["public_key"] = signer_public_key

        # Process the fields as needed
        account_type_str = fields.get("account_type")
        try:
            account_type = AccountType(account_type_str)
        except ValueError:
            raise InvalidTransaction(f"Invalid account type: {account_type_str}")
        account_class = self.account_types.get(account_type)

        if not account_class:
            raise InvalidTransaction(f"Unsupported account type: {account_type_str}")

        account = account_class.model_validate(fields)
        account_data = account.model_dump()

        account_address = self.address_generator.generate_account_address(account.public_key)

        if context.get_state([account_address]).get(account_address):
            raise InvalidTransaction("Account already exists")

        context.set_state({
            account_address: self.serialize_for_state(account_data)
        })

        event.add_data({
            "entity_address": account_address,
            "entity": account
        })

