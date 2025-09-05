from .. import BaseListener, EventContext, InvalidTransaction
from models.classes.accounts import BaseAccount
from models.enums import AccountType, SubEventType


class ValidateAssigneeAccount(BaseListener):
    def __init__(self):
        super().__init__([SubEventType.WORK_ORDER_CREATED], priorities=[-100])  # run after updating assignee history
        self.valid_assignees = [AccountType.ARTISAN] # add workshop later

    def on_event(self, event: EventContext):
        assignee: BaseAccount = event.get_data("assignee")

        if not assignee:
            raise InvalidTransaction("Assignee data not found in event context for ValidateAssigneeAccount")

        if assignee.account_type not in self.valid_assignees:
            raise InvalidTransaction(f"Account type {assignee.account_type} cannot create work orders")


