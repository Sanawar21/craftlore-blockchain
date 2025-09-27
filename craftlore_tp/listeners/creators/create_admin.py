from typing import Any


from .. import BaseListener, EventContext, InvalidTransaction
from models.enums import EventType, AdminPermissionLevel
from models.classes.accounts import (AdminAccount,)


class AdminCreationHandler(BaseListener):
    def __init__(self):
        super().__init__([EventType.ADMIN_CREATED], priorities=[1000]) # run before every other listener

    def on_event(self, event: EventContext):
        # Handle admin creation event
        context = event.context
        payload = event.payload
        signer_public_key = event.signer_public_key

        fields: dict[str, Any] = payload.get("fields")
        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")

        superadmin, superadmin_address = self.get_account(signer_public_key, event)
        if not isinstance(superadmin, AdminAccount) or superadmin.permission_level != AdminPermissionLevel.SUPER_ADMIN:
            raise InvalidTransaction("Only the super admin can mint admin accounts.")
        
        fields = fields.copy() 
        fields["created_timestamp"] = event.timestamp

        if fields.get("permission_level") == AdminPermissionLevel.SUPER_ADMIN:
            raise InvalidTransaction("Cannot create another super admin account.")

        new_admin = AdminAccount.model_validate(fields)
        for field in new_admin.forbidden_fields:
            if field in fields:
                raise InvalidTransaction(f"Field '{field}' cannot be set during account creation")

        account_address = self.address_generator.generate_account_address(new_admin.public_key)

        if context.get_state([account_address]):
            raise InvalidTransaction("Account already exists")
        
        # update super admin's history
        superadmin.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": signer_public_key,
            "targets": [new_admin.public_key],
            "transaction": event.signature,
            "timestamp": event.timestamp,
        })
        
        context.set_state({
            account_address: self.serialize_for_state(new_admin),
            superadmin_address: self.serialize_for_state(superadmin)
        })



        event.add_data({
            "entity": new_admin,
            "entity_address": account_address,
            "admin": superadmin,
            "admin_address": superadmin_address,
            "targets": event.get_data("targets", []).append(new_admin.public_key)
        })

