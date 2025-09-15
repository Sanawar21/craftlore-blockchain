from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import WorkOrder
from models.enums import AccountType, SubEventType, EventType, WorkOrderStatus

class AssigneeUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [SubEventType.WORK_ORDER_CREATED, EventType.WORK_ORDER_ACCEPTED, EventType.WORK_ORDER_REJECTED, EventType.WORK_ORDER_COMPLETED],
            priorities=[0, 1000, 1000, 1000]
        )  # default priority

    def on_event(self, event: EventContext):
        if event.event_type == SubEventType.WORK_ORDER_CREATED:
            entity: WorkOrder = event.get_data("entity")
            entity_address = event.get_data("entity_address")

            if not entity or not entity_address:
                raise InvalidTransaction("Entity data or address not found in event context for AssigneeUpdater")

            assignee, assignee_address = self.get_account(entity.assignee, event)
            assert isinstance(assignee, ArtisanAccount), "Assignee must be an ArtisanAccount"

            assignee.work_orders_assigned.append(entity.uid)
        
            targets = [entity.uid, assignee.public_key]

            assignee.history.append({
                "source": self.__class__.__name__,
                "event": event.event_type.value,
                "actor": event.signer_public_key,
                "targets": targets,
                "transaction": event.signature,
                "timestamp": event.timestamp
            })


            event.context.set_state({
                assignee_address: self.serialize_for_state(assignee)
            })

            event.add_data({
                "assignee_address": assignee_address,
                "assignee": assignee
            })
        
        elif event.event_type in {EventType.WORK_ORDER_ACCEPTED, EventType.WORK_ORDER_REJECTED, EventType.WORK_ORDER_COMPLETED}:
            context = event.context
            payload = event.payload
            signer_public_key = event.signer_public_key

            fields = payload.get("fields")
            if not fields:
                raise InvalidTransaction("Missing 'fields' key in payload for AssigneeUpdater")
            
            work_order_id = fields.get("work_order")
            if not work_order_id:
                raise InvalidTransaction("Missing 'work_order' in fields for AssigneeUpdater")          

            work_order, work_order_address = self.get_asset(work_order_id, event)
            assignee, assignee_address = self.get_account(signer_public_key, event)
            assert isinstance(work_order, WorkOrder), "Asset must be a WorkOrder"
            assert isinstance(assignee, ArtisanAccount), "Assignee must be an ArtisanAccount"
  
            if event.event_type == EventType.WORK_ORDER_ACCEPTED:

                assignee.work_orders_accepted.append(work_order.uid)

                if work_order.status != WorkOrderStatus.PENDING:
                    raise InvalidTransaction(f"Work order status must be 'pending' to accept, current status: {work_order.status}")

                work_order.status = WorkOrderStatus.ACCEPTED
                work_order.batch = fields.get("uid") # Link to created batch if any
                if not work_order.batch:
                    raise InvalidTransaction("Missing 'uid' for created batch in fields for AssigneeUpdater")

                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": [work_order.uid, fields.get("uid")],
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }

            elif event.event_type == EventType.WORK_ORDER_REJECTED:
                rejection_reason = fields.get("rejection_reason")
                if not rejection_reason:
                    raise InvalidTransaction("Missing 'rejection_reason' in fields for AssigneeUpdater")

                if work_order.status != WorkOrderStatus.PENDING:
                    raise InvalidTransaction(f"Work order status must be 'pending' to reject, current status: {work_order.status}")

                work_order.status = WorkOrderStatus.REJECTED
                work_order.rejection_reason = rejection_reason
                assignee.work_orders_rejected.append(work_order.uid)

                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": [work_order.uid],
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }

            elif event.event_type == EventType.WORK_ORDER_COMPLETED:
                if work_order.status != WorkOrderStatus.ACCEPTED:
                    raise InvalidTransaction(f"Work order status must be 'accepted' to complete, current status: {work_order.status}")
                
                assignee.work_orders_completed.append(work_order.uid)
                work_order.status = WorkOrderStatus.COMPLETED
                work_order.completion_date = event.timestamp

                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": [work_order.uid, work_order.batch],
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }                
            
            assignee.history.append(history_entry)
            work_order.history.append(history_entry)

            context.set_state({
                assignee_address: self.serialize_for_state(assignee),
                work_order_address: self.serialize_for_state(work_order)
            })


            event.add_data({
                "entity": work_order,
                "assignee": assignee
            })