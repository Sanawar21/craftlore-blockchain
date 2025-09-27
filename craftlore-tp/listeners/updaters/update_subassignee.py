from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import ArtisanAccount
from models.classes.assets import SubAssignment, ProductBatch
from models.enums import SubEventType, EventType, SubAssignmentStatus

class SubAssigneeUpdater(BaseListener):
    def __init__(self):
        super().__init__(
            [SubEventType.SUB_ASSIGNMENT_CREATED, EventType.SUBASSIGNMENT_ACCEPTED, EventType.SUBASSIGNMENT_REJECTED],
            priorities=[0, 1000, 1000]
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

        elif event.event_type in {EventType.SUBASSIGNMENT_ACCEPTED, EventType.SUBASSIGNMENT_REJECTED}:
            context = event.context
            payload = event.payload
            signer_public_key = event.signer_public_key

            fields = payload.get("fields")
            if not fields:
                raise InvalidTransaction("Missing 'fields' key in payload for AssigneeUpdater")

            assignment_id = fields.get("subassignment")
            if not assignment_id:
                raise InvalidTransaction("Missing 'subassignment' in fields for SubAssigneeUpdater")

            assignment, assignment_address = self.get_asset(assignment_id, event)
            assignee, assignee_address = self.get_account(signer_public_key, event)
            assert isinstance(assignment, SubAssignment), "Asset must be a SubAssignment"
            assert isinstance(assignee, ArtisanAccount), "Assignee must be an ArtisanAccount"
  
            if event.event_type == EventType.SUBASSIGNMENT_ACCEPTED:

                assignee.sub_assignments_accepted.append(assignment.uid)

                if assignment.status != SubAssignmentStatus.PENDING:
                    raise InvalidTransaction(f"Sub-assignment status must be 'pending' to accept, current status: {assignment.status}")

                assignment.status = SubAssignmentStatus.ACCEPTED

                # update batch too
                batch, batch_address = self.get_asset(assignment.batch, event)
                assert isinstance(batch, ProductBatch), "Sub-assigned batch must be a ProductBatch"

                batch.sub_assignments.append(assignment.uid)

                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": [assignment.uid, batch.uid],
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }

                # modify batch separately
                batch.history.append(history_entry)
                context.set_state({
                    batch_address: self.serialize_for_state(batch)
                })
                event.add_data({
                    "batch": batch,
                })

            
            elif event.event_type == EventType.SUBASSIGNMENT_REJECTED:
                assignee.sub_assignments_rejected.append(assignment.uid)

                if assignment.status != SubAssignmentStatus.PENDING:
                    raise InvalidTransaction(f"Sub-assignment status must be 'pending' to accept, current status: {assignment.status}")

                assignment.status = SubAssignmentStatus.REJECTED
                assignment.rejection_reason = fields.get("rejection_reason")
                if not assignment.rejection_reason:
                    raise InvalidTransaction("Missing 'rejection_reason' in fields for SubAssigneeUpdater")


                history_entry = {
                    "source": self.__class__.__name__,
                    "event": event.event_type.value,
                    "actor": event.signer_public_key,
                    "targets": [assignment.uid],
                    "transaction": event.signature,
                    "timestamp": event.timestamp
                }                

            assignee.history.append(history_entry)
            assignment.history.append(history_entry)

            context.set_state({
                assignee_address: self.serialize_for_state(assignee),
                assignment_address: self.serialize_for_state(assignment)
            })


            event.add_data({
                "entity": assignment,
                "assignee": assignee,
            })