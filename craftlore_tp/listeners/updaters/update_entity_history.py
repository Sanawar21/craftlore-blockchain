from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import BaseAsset
from models.enums import EventType, SubEventType

class EntityHistoryUpdater(BaseListener):
    """Updates entity history on creation"""
    def __init__(self):
        super().__init__(
            [EventType.ACCOUNT_CREATED, EventType.ASSET_CREATED, SubEventType.BATCH_CREATED, EventType.ADMIN_CREATED, EventType.CERTIFICATION_ISSUED],
            priorities=[0, 0, 0, 0, -100]
        )  # default priority

    def on_event(self, event: EventContext):
        entity: BaseAccount | BaseAsset = event.get_data("entity")
        entity_address = event.get_data("entity_address")

        if not entity or not entity_address:
            raise InvalidTransaction("Entity data or address not found in event context for EntityHistoryUpdater")

        entity.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [entity.uid] if isinstance(entity, BaseAsset) else [entity.public_key],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        event.context.set_state({
            entity_address: self.serialize_for_state(entity)
        })
