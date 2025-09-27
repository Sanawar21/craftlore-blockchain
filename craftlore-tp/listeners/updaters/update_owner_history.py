from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount, SupplierAccount
from models.classes.assets import BaseAsset, RawMaterial, WorkOrder
from models.enums import AccountType, AssetType, EventType, SubEventType

class OwnerHistoryUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.ASSET_CREATED, SubEventType.BATCH_CREATED, EventType.ADD_RAW_MATERIAL, SubEventType.LOGISTICS_CREATED, EventType.CERTIFICATION_ISSUED],
            priorities=[0, 0, 0, -100, 0]
        )  # default priority

    def on_event(self, event: EventContext):
        entity: BaseAsset = event.get_data("entity")

        if not entity:
            raise InvalidTransaction("Entity data not found in event context for OwnerHistoryUpdater")

        owner, owner_address = self.get_account(entity.asset_owner, event)

        if event.event_type in (EventType.ASSET_CREATED, SubEventType.BATCH_CREATED, SubEventType.LOGISTICS_CREATED, EventType.CERTIFICATION_ISSUED):
            owner.assets.append(entity.uid)
      
        targets = [entity.uid]

        if entity.asset_type == AssetType.RAW_MATERIAL.value and isinstance(entity, RawMaterial):
            assert isinstance(owner, SupplierAccount), "Owner must be a SupplierAccount for RawMaterial"
            owner.raw_materials_created.append(entity.uid)
        elif entity.asset_type == AssetType.WORK_ORDER.value and isinstance(entity, WorkOrder):
            targets.append(entity.assignee)
            owner.work_orders_issued.append(entity.uid)
        elif event.event_type == EventType.ADD_RAW_MATERIAL:
            targets.append(event.payload.get("fields").get("raw_material"))

        owner.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        })

        event.context.set_state({
            owner_address: self.serialize_for_state(owner)
        })

        event.add_data({
            "owner_address": owner_address,
            "owner": owner
        })
