from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import ProductBatch, RawMaterial, UsageRecord
from models.enums import AssetType, SubEventType, EventType, WorkOrderStatus, BatchStatus

class EditEntity(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ENTITY_EDITED],
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
            assert public_key == event.signer_public_key, "Cannot edit another user's account."
            entity, entity_address = self.get_account(public_key, event)
            targets = [entity.public_key]

        else:  # case_ == "asset":
            uid = fields.get("uid")
            entity, entity_address = self.get_asset(uid, event)
            assert entity.asset_owner == event.signer_public_key, "Cannot edit an asset you do not own."
            targets = [entity.uid]

            # update owner 
            signer, signer_address = self.get_account(event.signer_public_key, event)
            if uid in signer.assets:
                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": targets,
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }
                signer.history.append(history_entry)
                event.context.set_state({signer_address: self.serialize_for_state(signer)})
                event.add_data({"signer": signer})

        # common logic
        if entity.is_deleted:
            raise InvalidTransaction("Entity is deleted.")

        edits = {}

        for key, value in fields.get("updates", {}).items():
            if key not in entity.editable_fields:
                raise InvalidTransaction(f"Field '{key}' cannot be edited.")

            if isinstance(entity, RawMaterial):
                if entity.processor_public_key is not None:
                    raise InvalidTransaction("Cannot edit raw material after it has been processed.")
            
            old = getattr(entity, key)  # validate field existence
            setattr(entity, key, value)
            edits[key] = (old, value)

        history_entry = {
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp,
            "edits": edits
        }
        entity.history.append(history_entry)
        event.context.set_state({entity_address: self.serialize_for_state(entity)})
        event.add_data({"entity": entity})

