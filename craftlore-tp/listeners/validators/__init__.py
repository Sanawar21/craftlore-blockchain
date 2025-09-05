from .validate_creator_account import ValidateCreatorAccount
from .validate_assignee_account import ValidateAssigneeAccount

listeners = [
    ValidateCreatorAccount,
    ValidateAssigneeAccount,
]