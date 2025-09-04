from .. import BaseListener, EventType, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount, SupplierAccount
from models.classes.assets import BaseAsset, RawMaterial
from models.enums import AccountType, AssetType

class HistoryUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ACCOUNT_CREATED, EventType.ASSET_CREATED],
            priorities=[0, 0]
        )  # default priority

    def on_event(self, event: EventContext):
        entity = event.get_data("entity")
        entity_address = event.get_data("entity_address")

        if not entity or not entity_address:
            raise InvalidTransaction("Entity data or address not found in event context for HistoryUpdater")

        entity.history.append({
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [entity.uid] if isinstance(entity, BaseAsset) else [entity.public_key],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        event.context.set_state({
            entity_address: self.serialize_for_state(entity.model_dump())
        })
