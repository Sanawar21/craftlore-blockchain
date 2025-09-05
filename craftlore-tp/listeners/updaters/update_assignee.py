from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import WorkOrder
from models.enums import AccountType, SubEventType

class AssigneeUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [SubEventType.WORK_ORDER_CREATED],
            priorities=[0]
        )  # default priority

    def on_event(self, event: EventContext):
        entity: WorkOrder = event.get_data("entity")
        entity_address = event.get_data("entity_address")

        if not entity or not entity_address:
            raise InvalidTransaction("Entity data or address not found in event context for AssigneeUpdater")

        assignee_address = self.address_generator.generate_account_address(entity.assignee)
        entries = event.context.get_state([assignee_address])  # Ensure assignee account exists

        if entries:
            assignee_data = self.serializer.from_bytes(entries[0].data)
        else:
            raise InvalidTransaction("Assignee account does not exist for AssigneeUpdater")

        if assignee_data.get("account_type") == AccountType.ARTISAN.value:
            assignee: ArtisanAccount = self.account_types[AccountType.ARTISAN].model_validate(assignee_data)
        # add elif for workshop
        else:
            raise InvalidTransaction("Assignee must be an Artisan or Supplier account")

        assignee.work_orders_assigned.append(entity.uid)
      
        targets = [entity.uid, assignee.public_key]

        assignee.history.append({
            "event": event.event_type.value,
            "actor": event.signer_public_key,
            "targets": targets,
            "transaction": event.signature,
            "timestamp": event.timestamp
        })


        event.context.set_state({
            assignee_address: self.serialize_for_state(assignee.model_dump())
        })

        event.add_data({
            "assignee_address": assignee_address,
            "assignee": assignee
        })
