from .update_email_index import EmailIndexUpdater
from .update_owner_history import OwnerHistoryUpdater
from .update_entity_history import EntityHistoryUpdater
from .update_assignee import AssigneeUpdater

listeners = [
    EmailIndexUpdater,
    OwnerHistoryUpdater,
    EntityHistoryUpdater,
    AssigneeUpdater,
]