from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.classes.assets import WorkOrder
from models.enums import AccountType, SubEventType, EventType, WorkOrderStatus


class ValidateAcceptContext(BaseListener):
    def __init__(self):
        super().__init__([EventType.WORK_ORDER_ACCEPTED], priorities=[-100])  # run after updating acceptor history

    def on_event(self, event: EventContext):
        assignee: BaseAccount = event.get_data("assignee")
        entity: WorkOrder = event.get_data("entity")

        if not assignee:
            raise InvalidTransaction("Assignee data not found in event context for ValidateAcceptContext")

        if assignee.public_key != entity.assignee:
            raise InvalidTransaction("Acceptor must be the assignee of the work order")

        if assignee.is_deleted:
            raise InvalidTransaction("Assginee account is deleted")
        
        if entity.is_deleted:
            raise InvalidTransaction("Work order is deleted")

        # The following is getting checked in AssigneeUpdater already      
        # if entity.status != WorkOrderStatus.PENDING:
        #     raise InvalidTransaction(f"Work order status must be 'pending' to accept, current status: {entity.status}")



