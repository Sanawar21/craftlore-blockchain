from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import WorkOrder, ProductBatch
from models.enums import AccountType, SubEventType, EventType, WorkOrderStatus, BatchStatus

class BatchUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [EventType.WORK_ORDER_COMPLETED, EventType.BATCH_COMPLETED],
            priorities=[0, 0]
        )  # default priority

    def on_event(self, event: EventContext):

        if event.event_type == EventType.WORK_ORDER_COMPLETED:
            work_order: WorkOrder = event.get_data("entity")
            batch, batch_address = self.get_asset(work_order.batch, event)
            targets = [work_order.uid, batch.uid]
        elif event.event_type == EventType.BATCH_COMPLETED:
            batch: ProductBatch = event.get_data("entity")
            batch_address = self.address_generator.generate_asset_address(batch.uid)
            targets = [batch.uid]

        fields = event.payload.get("fields")        
        if not fields:
            raise InvalidTransaction("Missing 'fields' key in payload")
        
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
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        })
        event.context.set_state({
            batch_address: self.serialize_for_state(batch)
        })
        event.add_data({
            "batch": batch
        })
