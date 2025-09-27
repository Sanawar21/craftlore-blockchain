from .. import BaseListener, EventContext, InvalidTransaction
from models.enums import EventType

class DeleteEntity(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ENTITY_DELETED],
            priorities=[1000]
        )  # default priority

    def on_event(self, event: EventContext):
        payload = event.payload
        fields = payload.get("fields", {})
        case_ = "asset" if "uid" in fields else "account" if "public_key" in fields else None

        if case_ is None:
            raise InvalidTransaction("Either 'uid' or 'public_key' must be provided to identify the entity to delete.")
        if "deletion_reason" not in fields:
            raise InvalidTransaction("A reason for deletion must be provided.")
        
        reason = fields.get("deletion_reason")

        if case_ == "account":
            public_key = fields.get("public_key")
            assert public_key == event.signer_public_key, "Cannot delete another user's account."
            entity, entity_address = self.get_account(public_key, event)
            targets = [entity.public_key]

        elif case_ == "asset":
            uid = fields.get("uid")
            entity, entity_address = self.get_asset(uid, event)
            assert entity.asset_owner == event.signer_public_key, "Cannot delete an asset you do not own."
            targets = [entity.uid]

            # update owner 
            # remove asset from owners's assets list
            signer, signer_address = self.get_account(event.signer_public_key, event)
            if uid in signer.assets:
                signer.assets.remove(uid)
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
            raise InvalidTransaction("Entity is already deleted.")
        entity.is_deleted = True
        entity.deletion_reason = reason
        history_entry = {
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        }
        entity.history.append(history_entry)
        event.context.set_state({entity_address: self.serialize_for_state(entity)})
        event.add_data({"entity": entity})

