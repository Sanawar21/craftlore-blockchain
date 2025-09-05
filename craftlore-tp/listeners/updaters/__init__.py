from .update_email_index import EmailIndexUpdater
from .update_owner_history import OwnerHistoryUpdater
from .update_history import HistoryUpdater
from .update_assignee import AssigneeUpdater

listeners = [
    EmailIndexUpdater,
    OwnerHistoryUpdater,
    HistoryUpdater,
    AssigneeUpdater,
]