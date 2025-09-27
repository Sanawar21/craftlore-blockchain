from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import ProductBatch
from models.enums import EventType


class ValidateBatchCompletion(BaseListener):
    def __init__(self):
        super().__init__([EventType.BATCH_COMPLETED],
                          priorities=[-100])  

    def on_event(self, event: EventContext):
        assignee: ArtisanAccount = event.get_data("assignee")
        entity: ProductBatch = event.get_data("entity")

        if not assignee:
            raise InvalidTransaction("Assignee data not found in event context for ValidateBatchCompletion")

        if assignee.public_key != entity.asset_owner:
            raise InvalidTransaction("Producer must be the owner of the batch")

        if assignee.is_deleted:
            raise InvalidTransaction("Producer account is deleted")

        if entity.is_deleted:
            raise InvalidTransaction("Batch is deleted")

        if entity.work_order is not None:
            raise InvalidTransaction("Batch linked to a work order cannot be completed directly")

        # The following is getting checked in AssigneeUpdater and BatchUpdater already      
        # if entity.status != WorkOrderStatus.PENDING:
        #     raise InvalidTransaction(f"Work order status must be 'pending' to accept, current status: {entity.status}")



