from typing import Any

from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import SubAssignment
from models.enums import AccountType, SubEventType, EventType, SubAssignmentStatus

class SubAssigneeUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [SubEventType.SUB_ASSIGNMENT_CREATED],
            priorities=[0]
        )  # default priority

    def on_event(self, event: EventContext):
        if event.event_type == SubEventType.SUB_ASSIGNMENT_CREATED:
            assignment: SubAssignment = event.get_data("entity")
            assignment_address = event.get_data("entity_address")

            if not assignment or not assignment_address:
                raise InvalidTransaction("SubAssignment or address not found in event context for SubAssigneeUpdater")

            assignee, assignee_address = self.get_account(assignment.assignee, event)
            assert isinstance(assignee, ArtisanAccount), "Assignee must be an ArtisanAccount"

            assignee.sub_assignments.append(assignment.uid)

            targets = [assignment.uid, assignee.public_key]

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
        