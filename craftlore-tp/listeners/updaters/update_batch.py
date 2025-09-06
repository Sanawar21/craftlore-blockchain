from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import WorkOrder, ProductBatch
from models.enums import AccountType, SubEventType, EventType, WorkOrderStatus, BatchStatus

class BatchUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.WORK_ORDER_COMPLETED],
            priorities=[0]
        )  # default priority

    def on_event(self, event: EventContext):
        work_order: WorkOrder = event.get_data("entity")
        batch_address = self.address_generator.generate_asset_address(work_order.batch)
        entries = event.context.get_state([batch_address])
        if entries:
            batch_data = self.serializer.from_bytes(entries[0].data)
        else:
            raise InvalidTransaction("Batch does not exist for BatchUpdater")

        fields = event.payload.get("fields")
        
        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")
        
        batch = ProductBatch.model_validate(batch_data)
        batch.production_date = event.timestamp
        batch.status = BatchStatus.COMPLETED
        batch.quantity = fields.get("quantity", batch.quantity)
        batch.units_produced = fields.get("units_produced")

        if batch.units_produced is None:
            raise InvalidTransaction("Missing 'units_produced' in payload fields")

        batch.history.append({
            "source": self.__class__.__name__,
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": [batch.uid, work_order.uid],
            "transaction": event.signature,
            "timestamp": event.timestamp
        })
        event.context.set_state({
            batch_address: self.serialize_for_state(batch.model_dump())
        })
        event.add_data({
            "batch": batch
        })
