from typing import List

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.base_class import BaseClass
from models.classes.accounts import AdminAccount 
from models.enums import AssetType, SubEventType, EventType, AdminAccountStatus, AdminPermissionLevel

class ModeratorEdit(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.MODERATOR_EDIT],
            priorities=[1000]
        )  # default priority

    def __apply_edits(self, entity: BaseClass, edits: dict):
        """Recursively apply edits (including nested dicts) to an entity."""
        for key, value in edits.items():

            current_val = getattr(entity, key, None)

            if isinstance(value, dict):
                if isinstance(current_val, dict):
                    # Merge into dict attribute
                    for subkey, subval in value.items():
                        current_val[subkey] = subval
                else:
                    # If entity field is an object, recurse
                    self.__apply_edits(current_val, value)
            else:
                setattr(entity, key, value)

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})

        edits: List[dict] = fields.get("updates")

        assert isinstance(edits, dict) and all(isinstance(edit, dict) for edit in edits.values()), "'updates' must be a dictionary of dictionaries"

        moderator, moderator_address = self.get_account(event.signer_public_key, event)
        assert isinstance(moderator, AdminAccount), "Moderator must be an admin account. Got {}".format(type(moderator))

        for address, edit in edits.items():
            if "-" in address:
                entity, entity_address = self.get_asset(address, event)
            else:
                entity, entity_address = self.get_account(address, event)
                assert not isinstance(entity, AdminAccount), "Cannot edit admin accounts"

            assert "history" not in edit, "Cannot edit 'history' field"

            self.__apply_edits(entity, edit)

            history_entry = {
                "source": self.__class__.__name__,
                "event": event.event_type.value,
                "actor": event.signer_public_key,
                "targets": [entity.uid] if hasattr(entity, 'uid') else [entity.public_key],
                "transaction": event.signature,
                "timestamp": event.timestamp,
            }
            entity.history.append(history_entry)

            event.context.set_state({entity_address: self.serialize_for_state(entity)})
        
        moderator.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": list(edits.keys()),
            "transaction": event.signature,
            "timestamp": event.timestamp,
          })

        event.add_data({
            "admin_address": moderator_address,
            "admin": moderator,
        })