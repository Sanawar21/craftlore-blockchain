from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import AdminAccount
from models.enums import EventType, AdminPermissionLevel, AuthenticationStatus

class AuthenticateEntity(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ENTITY_AUTHENTICATED],
            priorities=[1000]
        )  # default priority

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})
        case_ = "asset" if "uid" in fields else "account" if "public_key" in fields else None

        if case_ is None:
            raise InvalidTransaction("Either 'uid' or 'public_key' must be provided to identify the entity to edit.")
        
        if case_ == "account":
            public_key = fields.get("public_key")
            entity, entity_address = self.get_account(public_key, event)
            targets = [entity.public_key]

        else:  # case_ == "asset":
            uid = fields.get("uid")
            entity, entity_address = self.get_asset(uid, event)
            targets = [entity.uid]

        if isinstance(entity, AdminAccount):
            if entity.permission_level == AdminPermissionLevel.SUPER_ADMIN:
                raise InvalidTransaction("Cannot change authentication status of super admin account.")
            assert entity.public_key != event.signer_public_key, "Cannot authenticate your own admin account."
            

        # common logic
        if entity.is_deleted:
            raise InvalidTransaction("Entity is deleted.")

        entity.authentication_status = AuthenticationStatus(fields.get("authentication_status"))

        authenticator, authenticator_address = self.get_account(event.signer_public_key, event)
        assert isinstance(authenticator, AdminAccount), f"Authenticator must be an admin account. Got {type(authenticator)}"

        
        history_entry = {
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp,
        }
        entity.history.append(history_entry)
        authenticator.history.append(history_entry)

        event.context.set_state({entity_address: self.serialize_for_state(entity)})
        event.add_data({"entity": entity, "admin": authenticator, "admin_address": authenticator_address})

