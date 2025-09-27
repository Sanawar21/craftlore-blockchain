from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import AdminAccount
from models.enums import EventType

class AdminActionsUpdater(BaseListener):
    """Updates admin actions on admin events"""
    def __init__(self):
        super().__init__(
            [EventType.ADMIN_CREATED, EventType.CERTIFICATION_ISSUED, EventType.EDITED_BY_MODERATOR, EventType.ENTITY_AUTHENTICATED],
            priorities=[0, -300, -300, -300]  
        )  # default priority

    def on_event(self, event: EventContext):
        admin: AdminAccount = event.get_data("admin")
        admin_address = event.get_data("admin_address")
        details = event.payload.get("fields", {}).get("action_details")

        assert isinstance(details, str), "Action details must be a string"

        if not details:
            raise InvalidTransaction("No action details provided in event payload")

        if not admin or not admin_address:
            raise InvalidTransaction("Admin data or address not found in event context for AdminActionsUpdater")

        admin.actions.append(
            {
                "details": details,
                "transaction": event.signature,
                "timestamp": event.timestamp
            }
        )

        event.context.set_state({
            admin_address: self.serialize_for_state(admin)
        })
